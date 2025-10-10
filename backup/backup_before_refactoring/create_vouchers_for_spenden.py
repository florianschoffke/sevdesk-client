#!/usr/bin/env python3
"""
Create vouchers for Spenden (Donations) transactions.

This script finds open incoming transactions (amount > 0) with donation-related keywords
in the payment purpose and creates vouchers for them.

Donation keywords: "Spende", "SPENDE", "Tobi Zimmermann", "Unterstützung", "Gemeindespende",
"für die Gemeinde", "MONATLICHE SPENDE", "GEMEINDE", "Spends", "Offering", 
starts with "Monatsspende", "GEMEINDE SPENDE"

Four types of donations:
1. Mission donations: purpose contains "Mission" or "Missionar" 
   → Cost Centre: "Spendeneingänge Missionare"
2. Jeske donations: purpose contains "Artur Jeske"
   → Cost Centre: "Jeske (Durchlaufende Posten)"
3. Tobias donations: purpose contains "Spende Tobias Zimmermann" or "Tobi Zimmermann"
   → Cost Centre: "Tobias Zimmermann (Spende für Tobias)"
4. General donations: all others (including "Unterstützung", "Gemeindespende", etc.)
   → Cost Centre: "Spendeneingänge Konto"
   
All use Accounting Type: "Spendeneingang"
"""
import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv
from sevdesk.client import SevDeskClient
from database.db import TransactionDB
from reload_data import reload_all_data
from voucher_utils import (
    generate_voucher_numbers,
    build_voucher_plan_markdown,
    print_console_summary,
    print_voucher_table,
    find_contact_by_name,
    create_voucher_for_transaction
)


# Cost centre names for different donation types
COST_CENTRE_NAMES = {
    'mission': 'Spendeneingänge Missionare',
    'general': 'Spendeneingänge Konto',
    'jeske': 'Jeske (Durchlaufende Posten)',
    'tobias': 'Tobias Zimmermann (Spende für Tobias)',
}


def find_cost_centre_by_exact_name(db: TransactionDB, name: str) -> dict:
    """Find a cost centre by exact name match."""
    if not name:
        return None
    
    all_cost_centres = db.get_all_cost_centres()
    for cc in all_cost_centres:
        if cc.get('name') == name:
            return cc
    return None


def determine_donation_type_and_cost_centre(
    db: TransactionDB,
    payment_purpose: str,
    cost_centres: dict
) -> tuple:
    """
    Determine donation type and select appropriate cost centre.
    
    Args:
        db: Database connection
        payment_purpose: Payment purpose text
        cost_centres: Dict with keys: mission, general, jeske, tobias
        
    Returns:
        Tuple of (donation_type, cost_centre)
    """
    if not payment_purpose:
        return ('general', cost_centres['general'])
    
    purpose = payment_purpose
    purpose_lower = payment_purpose.lower()
    
    # Special rules for specific donation purposes (checked first)
    if 'Artur Jeske' in purpose:
        return ('jeske', cost_centres['jeske'])
    
    # Check for Tobias Zimmermann donations (multiple patterns)
    if 'Spende Tobias Zimmermann' in purpose or 'Tobi Zimmermann' in purpose:
        return ('tobias', cost_centres['tobias'])
    
    # Check for mission-related keywords
    if 'mission' in purpose_lower or 'missionar' in purpose_lower:
        return ('mission', cost_centres['mission'])
    
    # Default: general donation
    return ('general', cost_centres['general'])


def find_spenden_contact(db: TransactionDB, payee_name: str) -> dict:
    """
    Find contact for Spenden (prefer Customers for income).
    Uses enhanced matching with first-name prioritization for multi-name payees.
    """
    return find_contact_by_name(db, payee_name, prefer_category=2)


def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create vouchers for Spenden transactions')
    parser.add_argument('--create-single', action='store_true', 
                       help='Create a single voucher (for testing)')
    parser.add_argument('--create-all', action='store_true',
                       help='Create all vouchers')
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('SEVDESK_API_KEY')
    api_url = os.getenv('SEVDESK_API_URL', 'https://my.sevdesk.de/api/v1')
    db_path = os.getenv('DB_PATH', 'transactions.db')
    
    if not api_key:
        print("Error: SEVDESK_API_KEY not found in environment variables.")
        sys.exit(1)
    
    print("=" * 80)
    print("Spenden Voucher Creator")
    print("=" * 80)
    print()
    
    # Reload all data from API first
    print("Reloading all data from SevDesk API...")
    print()
    if not reload_all_data(db_path=db_path, api_key=api_key, api_url=api_url):
        print("Error: Failed to reload data from API")
        sys.exit(1)
    print()
    print("=" * 80)
    print()
    
    # Initialize API client early (needed for voucher numbering)
    print(f"Connecting to SevDesk API at {api_url}...")
    client = SevDeskClient(api_key=api_key, base_url=api_url)
    print("✓ Connected")
    print()
    
    # Initialize database
    print(f"Opening database: {db_path}")
    with TransactionDB(db_path=db_path) as db:
        # Get accounting type for Spendeneingang
        accounting_type = None
        all_accounting_types = db.get_all_accounting_types()
        for at in all_accounting_types:
            if 'Spendeneingang' in at.get('name', ''):
                accounting_type = at
                break
        
        if not accounting_type:
            print("Error: Could not find 'Spendeneingang' accounting type!")
            sys.exit(1)
        
        print(f"✓ Found accounting type: {accounting_type['name']} (ID: {accounting_type['id']})")
        print()
        
        # Get cost centres for all donation types
        cost_centres = {}
        missing_cost_centres = []
        
        for donation_type, cc_name in COST_CENTRE_NAMES.items():
            cc = find_cost_centre_by_exact_name(db, cc_name)
            if cc:
                cost_centres[donation_type] = cc
                print(f"✓ Found cost centre ({donation_type}): {cc['name']} (ID: {cc['id']})")
            else:
                missing_cost_centres.append(cc_name)
                print(f"❌ Missing cost centre ({donation_type}): {cc_name}")
        
        print()
        
        if missing_cost_centres:
            print("Error: Required cost centres not found:")
            for cc_name in missing_cost_centres:
                print(f"  - {cc_name}")
            sys.exit(1)
        
        # Get all open transactions with positive amounts (income)
        print("Fetching open transactions...")
        all_transactions = db.get_all_transactions(status=100)
        print(f"✓ Found {len(all_transactions)} open transactions")
        print()
        
        # Filter transactions with Spende and positive amount (income)
        spenden_transactions = []
        for txn in all_transactions:
            payment_purpose = txn.get('paymt_purpose', '') or ''
            amount = float(txn.get('amount', 0))
            
            # Must be income (positive) and match one of the donation patterns
            if amount > 0:
                is_spende = (
                    'Spende' in payment_purpose or 
                    'SPENDE' in payment_purpose or
                    'Tobi Zimmermann' in payment_purpose or
                    'Unterstützung' in payment_purpose or
                    'Unterstuetzung' in payment_purpose or
                    'Gemeindespende' in payment_purpose or
                    'für die Gemeinde' in payment_purpose or
                    'MONATLICHE SPENDE' in payment_purpose or
                    'GEMEINDE' in payment_purpose or
                    'Spends' in payment_purpose or
                    'Offering' in payment_purpose or
                    payment_purpose.startswith('Monatsspende') or
                    'GEMEINDE SPENDE' in payment_purpose
                )
                
                if is_spende:
                    spenden_transactions.append(txn)
        
        print(f"✓ Found {len(spenden_transactions)} donation transactions")
        print()
        
        if not spenden_transactions:
            print("No matching transactions found. Exiting.")
            return
        
        # Generate voucher numbers for all transactions
        print("Generating voucher numbers...")
        voucher_numbers = generate_voucher_numbers(client, len(spenden_transactions))
        print(f"✓ Generated {len(voucher_numbers)} voucher numbers (starting from: {voucher_numbers[0]})")
        print()
        
        # Build voucher plan
        voucher_plan = []
        for i, txn in enumerate(spenden_transactions):
            # Parse raw data to get payeePayerName
            raw_data = json.loads(txn.get('raw_data', '{}'))
            payee_payer_name = raw_data.get('payeePayerName', 'Unknown')
            
            # Determine donation type and cost centre
            donation_type, cost_centre = determine_donation_type_and_cost_centre(
                db, txn.get('paymt_purpose'), cost_centres
            )
            
            # Find matching contact (donor) - IMPORTANT!
            contact = find_spenden_contact(db, payee_payer_name)
            
            # Get voucher number from pre-generated list
            voucher_number = voucher_numbers[i]
            
            voucher_plan.append({
                'transaction_id': txn['id'],
                'transaction_date': txn['value_date'],
                'amount': txn['amount'],
                'payment_purpose': txn['paymt_purpose'],
                'payee_payer_name': payee_payer_name,
                'donation_type': donation_type,
                'cost_centre': cost_centre,
                'contact': contact,
                'voucher_number': voucher_number,
                'accounting_type': accounting_type
            })
        
        # Count donation types
        type_counts = {
            'mission': sum(1 for p in voucher_plan if p['donation_type'] == 'mission'),
            'general': sum(1 for p in voucher_plan if p['donation_type'] == 'general'),
            'jeske': sum(1 for p in voucher_plan if p['donation_type'] == 'jeske'),
            'tobias': sum(1 for p in voucher_plan if p['donation_type'] == 'tobias'),
        }
        
        # Build extra sections for markdown
        extra_sections = []
        extra_sections.append("## Donation Type Statistics")
        extra_sections.append("")
        extra_sections.append(f"- 🎯 Mission donations: {type_counts['mission']}")
        extra_sections.append(f"- 💝 General donations: {type_counts['general']}")
        extra_sections.append(f"- 🔄 Jeske donations: {type_counts['jeske']}")
        extra_sections.append(f"- 👤 Tobias donations: {type_counts['tobias']}")
        extra_sections.append(f"- **Total**: {len(voucher_plan)} donations")
        extra_sections.append("")
        
        # Build markdown content using shared utility
        markdown_lines = build_voucher_plan_markdown(
            title="Spenden Voucher Plan",
            voucher_plan=voucher_plan,
            accounting_type=accounting_type,
            extra_sections=extra_sections,
            show_donation_type=True
        )
        
        # Write to file
        output_file = "voucher_plan_spenden.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_lines))
        
        # Get counts for summary
        missing_contacts = [p for p in voucher_plan if not p['contact']]
        
        # If no create flag, just show the plan
        if not args.create_single and not args.create_all:
            # Display summary to console
            print("=" * 80)
            print("VOUCHER PLAN GENERATED")
            print("=" * 80)
            print()
            print(f"✓ Plan saved to: {output_file}")
            print(f"✓ Total vouchers to create: {len(voucher_plan)}")
            print()
            
            print("Donation Type Breakdown:")
            print(f"  🎯 Mission: {type_counts['mission']}")
            print(f"  💝 General: {type_counts['general']}")
            print(f"  🔄 Jeske: {type_counts['jeske']}")
            print(f"  👤 Tobias: {type_counts['tobias']}")
            print()
            
            if missing_contacts:
                print(f"⚠️  WARNING: {len(missing_contacts)} transaction(s) have no matching contact")
                print("   Donations MUST be linked to contacts for tax tracking!")
                print("   See the markdown file for details.")
                print()
            
            print("Accounting Type for all positions:")
            print(f"  → {accounting_type['name']} (ID: {accounting_type['id']})")
            print()
            print("Next steps:")
            print(f"  1. Open and review: {output_file}")
            print("  2. Test with single voucher: python create_vouchers_for_spenden.py --create-single")
            print("  3. Create all vouchers: python create_vouchers_for_spenden.py --create-all")
            print()
            print("=" * 80)
            return
        
        # Show the markdown plan before creating
        print("=" * 80)
        print("VOUCHER PLAN REVIEW")
        print("=" * 80)
        print()
        print(f"📄 Plan file: {output_file}")
        print()
        
        # Display the plan in a table format using shared utility
        print_voucher_table(
            voucher_plan=voucher_plan,
            create_all=args.create_all,
            show_donation_type=True
        )
        print(f"Total: {len(voucher_plan) if args.create_all else 1} voucher(s) will be created")
        print()
        
        # Ask for confirmation
        print("⚠️  Please review the voucher plan above carefully!")
        print()
        response = input("Do you want to proceed with creating these vouchers? (y/N): ").strip().lower()
        
        if response != 'y':
            print()
            print("❌ Cancelled by user. No vouchers were created.")
            print()
            print("=" * 80)
            return
        
        print()
        
        # Create vouchers
        print("=" * 80)
        print("CREATING VOUCHERS")
        print("=" * 80)
        print()
        
        # Get check account ID from first transaction
        first_txn_raw = json.loads(spenden_transactions[0].get('raw_data', '{}'))
        check_account_id = first_txn_raw.get('checkAccount', {}).get('id')
        sev_client_id = first_txn_raw.get('sevClient', {}).get('id')
        
        # Determine which vouchers to create
        vouchers_to_create = [voucher_plan[0]] if args.create_single else voucher_plan
        
        print(f"Creating {len(vouchers_to_create)} voucher(s)...")
        print()
        
        created_vouchers = []
        failed_vouchers = []
        
        for i, plan in enumerate(vouchers_to_create, 1):
            # Icons: 🎯=mission, 🔄=jeske, 👤=tobias, 💝=general
            if plan['donation_type'] == 'mission':
                type_icon = "🎯"
            elif plan['donation_type'] == 'jeske':
                type_icon = "🔄"
            elif plan['donation_type'] == 'tobias':
                type_icon = "👤"
            else:
                type_icon = "💝"
            
            print(f"[{i}/{len(vouchers_to_create)}] Creating voucher for transaction {plan['transaction_id']}...")
            print(f"    Amount: €{plan['amount']:,.2f}")
            print(f"    Donor: {plan['payee_payer_name']}")
            print(f"    Type: {type_icon} {plan['donation_type']}")
            print(f"    Cost Centre: {plan['cost_centre']['name']}")
            print(f"    Contact: {plan['contact']['name'] if plan['contact'] else 'None'}")
            
            try:
                response = create_voucher_for_transaction(
                    client, plan, check_account_id, sev_client_id, is_income=True
                )
                
                if response and 'objects' in response:
                    # Extract voucher ID from nested structure
                    voucher_id = response['objects'].get('voucher', {}).get('id')
                    print(f"    ✓ Voucher created successfully! ID: {voucher_id}")
                    
                    # Book voucher amount to link it to the transaction
                    print(f"    Booking voucher amount to link to transaction...")
                    try:
                        book_response = client.book_voucher_amount(
                            voucher_id=voucher_id,
                            transaction_id=plan['transaction_id'],
                            check_account_id=check_account_id,
                            amount=plan['amount'],
                            date=plan['transaction_date'][:10],
                            is_income=True
                        )
                        print(f"    ✓ Voucher booked and linked to transaction!")
                    except Exception as link_error:
                        print(f"    ⚠️  Warning: Failed to book/link voucher: {str(link_error)}")
                    
                    created_vouchers.append({
                        'plan': plan,
                        'voucher_id': voucher_id,
                        'response': response
                    })
                else:
                    print(f"    ❌ Failed: Unexpected response format")
                    failed_vouchers.append(plan)
                    
            except Exception as e:
                print(f"    ❌ Failed: {str(e)}")
                failed_vouchers.append(plan)
            
            print()
        
        # Summary
        print("=" * 80)
        print("CREATION SUMMARY")
        print("=" * 80)
        print()
        print(f"✓ Successfully created: {len(created_vouchers)} voucher(s)")
        if failed_vouchers:
            print(f"❌ Failed: {len(failed_vouchers)} voucher(s)")
        print()
        
        # Verify transaction statuses
        if created_vouchers:
            print("Verifying transaction statuses...")
            print()
            
            # Reload transactions from API
            print("Reloading transactions from API...")
            try:
                updated_transactions = client.get_all_transactions(status=None)
                print(f"✓ Loaded {len(updated_transactions)} transactions")
                print()
                
                # Check each created voucher's transaction
                for created in created_vouchers:
                    txn_id = created['plan']['transaction_id']
                    txn = next((t for t in updated_transactions if t.get('id') == txn_id), None)
                    
                    if txn:
                        old_status = 100  # Was open
                        new_status = txn.get('status')
                        status_name = {100: 'Open', 200: 'Linked', 1000: 'Booked'}.get(new_status, f'Unknown ({new_status})')
                        
                        if new_status != old_status:
                            print(f"✓ Transaction {txn_id}: {old_status} → {new_status} ({status_name})")
                        else:
                            print(f"⚠️  Transaction {txn_id}: Still at status {new_status} ({status_name})")
                    else:
                        print(f"❌ Transaction {txn_id}: Not found in updated data")
                
                print()
                
                # Update database
                print("Updating local database...")
                with TransactionDB(db_path=db_path) as db_update:
                    inserted = db_update.bulk_insert_transactions(updated_transactions)
                    print(f"✓ Updated {inserted} transactions in database")
                print()
                
            except Exception as e:
                print(f"❌ Error during verification: {str(e)}")
                print()
        
        print("=" * 80)
        print("DONE")
        print("=" * 80)


if __name__ == '__main__':
    main()
