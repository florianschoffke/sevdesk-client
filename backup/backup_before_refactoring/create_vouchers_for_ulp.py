#!/usr/bin/env python3
"""
Create vouchers for ÜLP (Übungsleiterpauschale) transactions.

This script finds open transactions containing "ÜLP" or "Übungsleiterpauschale"
in the payment purpose and creates vouchers for them.
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sevdesk.client import SevDeskClient
from database.db import TransactionDB
from reload_data import reload_all_data
from voucher_utils import (
    build_voucher_plan_markdown,
    print_console_summary,
    print_voucher_table,
    find_cost_centre_by_name,
    find_contact_by_name,
    create_voucher_for_transaction,
    generate_voucher_numbers
)


# Custom mappings for ÜLP script
COST_CENTRE_MAPPINGS = {
    'tobias zimmermann': 'tobias zimmermann (ülp)',  # Special rule for ÜLP
}

CONTACT_MAPPINGS = {
    # Add any custom contact mappings here if needed
}


def find_ulp_cost_centre(db: TransactionDB, payee_name: str, is_ulp_transaction: bool = False) -> dict:
    """
    Find cost centre for ÜLP transactions with special rules.
    
    Args:
        db: Database connection
        payee_name: Name to search for
        is_ulp_transaction: Whether this is a ÜLP transaction
        
    Returns:
        Cost centre dict or None
    """
    # Special rule: For Tobias Zimmermann + ÜLP transaction, use "Tobias Zimmermann (ÜLP)"
    mappings = COST_CENTRE_MAPPINGS if is_ulp_transaction else {}
    return find_cost_centre_by_name(db, payee_name, custom_mappings=mappings)


def find_ulp_contact(db: TransactionDB, payee_name: str) -> dict:
    """
    Find contact for ÜLP transactions (prefer Suppliers for expenses).
    
    Args:
        db: Database connection
        payee_name: Name to search for
        
    Returns:
        Contact dict or None
    """
    return find_contact_by_name(db, payee_name, prefer_category=3, custom_mappings=CONTACT_MAPPINGS)


def main():
    """Main function."""
    import json
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create vouchers for ÜLP transactions')
    parser.add_argument('--create-single', action='store_true', 
                       help='Create voucher for the first transaction only (test mode)')
    parser.add_argument('--create-all', action='store_true',
                       help='Create vouchers for all transactions')
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('SEVDESK_API_KEY')
    api_url = os.getenv('SEVDESK_API_URL', 'https://my.sevdesk.de/api/v1')
    db_path = os.getenv('DB_PATH', 'transactions.db')
    
    # Validate API key
    if not api_key:
        print("Error: SEVDESK_API_KEY not found in environment variables.")
        sys.exit(1)
    
    print("=" * 80)
    print("ÜLP Voucher Creator")
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
        # Get accounting type for Ehrenamtspauschale
        accounting_type = None
        all_accounting_types = db.get_all_accounting_types()
        for at in all_accounting_types:
            if 'Ehrenamtspauschale' in at.get('name', '') or 'Übungsleiterpauschale' in at.get('name', ''):
                accounting_type = at
                break
        
        if not accounting_type:
            print("Error: Could not find 'Ehrenamtspauschale/Übungsleiterpauschale' accounting type!")
            sys.exit(1)
        
        print(f"✓ Found accounting type: {accounting_type['name']} (ID: {accounting_type['id']})")
        print()
        
        # Get all open transactions
        print("Fetching open transactions...")
        all_transactions = db.get_all_transactions(status=100)
        print(f"✓ Found {len(all_transactions)} open transactions")
        print()
        
        # Filter transactions with ÜLP or Übungsleiterpauschale
        ulp_transactions = []
        for txn in all_transactions:
            payment_purpose = txn.get('paymt_purpose', '') or ''
            payment_purpose_lower = payment_purpose.lower()
            if ('ülp' in payment_purpose_lower or 
                'übungsleiterpauschale' in payment_purpose_lower or
                'ehrenamtspauschale' in payment_purpose_lower):
                ulp_transactions.append(txn)
        
        print(f"✓ Found {len(ulp_transactions)} transactions matching 'ÜLP', 'Übungsleiterpauschale' or 'Ehrenamtspauschale'")
        print()
        
        if not ulp_transactions:
            print("No matching transactions found. Exiting.")
            return
        
        # Generate voucher numbers for all transactions
        print("Generating voucher numbers...")
        voucher_numbers = generate_voucher_numbers(client, len(ulp_transactions))
        print(f"✓ Generated {len(voucher_numbers)} voucher numbers (next available: {voucher_numbers[0]})")
        print()
        
        # Build voucher plan
        voucher_plan = []
        for i, txn in enumerate(ulp_transactions):
            # Parse raw data to get payeePayerName
            import json
            raw_data = json.loads(txn.get('raw_data', '{}'))
            payee_payer_name = raw_data.get('payeePayerName', 'Unknown')
            
            # Check if this is a ÜLP transaction
            payment_purpose = txn.get('paymt_purpose', '') or ''
            is_ulp = 'ÜLP' in payment_purpose
            
            # Find matching cost centre (with special rule for Tobias + ÜLP)
            cost_centre = find_ulp_cost_centre(db, payee_payer_name, is_ulp_transaction=is_ulp)
            
            # Find matching contact (supplier)
            contact = find_ulp_contact(db, payee_payer_name)
            
            # Get voucher number from pre-generated list
            voucher_number = voucher_numbers[i]
            
            voucher_plan.append({
                'transaction_id': txn['id'],
                'transaction_date': txn['value_date'],
                'amount': txn['amount'],
                'payment_purpose': txn['paymt_purpose'],
                'payee_payer_name': payee_payer_name,
                'cost_centre': cost_centre,
                'contact': contact,
                'voucher_number': voucher_number,
                'accounting_type': accounting_type
            })
        
        # Build markdown content using shared utility
        markdown_lines = build_voucher_plan_markdown(
            title="ÜLP Voucher Plan",
            voucher_plan=voucher_plan,
            accounting_type=accounting_type,
            show_donation_type=False
        )
        
        # Write to file
        output_file = "voucher_plan.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_lines))
        
        # Get counts for summary
        missing_cost_centres = [p for p in voucher_plan if not p['cost_centre']]
        missing_contacts = [p for p in voucher_plan if not p['contact']]
        
        # If no create flag, just show the plan
        if not args.create_single and not args.create_all:
            # Display summary to console using shared utility
            print_console_summary(
                title="ÜLP Voucher Creator",
                output_file=output_file,
                voucher_count=len(voucher_plan),
                accounting_type=accounting_type,
                missing_cost_centres=len(missing_cost_centres),
                missing_contacts=len(missing_contacts),
                script_name="create_vouchers_for_ulp.py"
            )
            
            if missing_cost_centres:
                print(f"⚠️  WARNING: {len(missing_cost_centres)} transaction(s) have no matching cost centre")
                print("   See the markdown file for details.")
                print()
            
            if missing_contacts:
                print(f"⚠️  WARNING: {len(missing_contacts)} transaction(s) have no matching contact")
                print("   See the markdown file for details.")
                print()
            
            print("Accounting Type for all positions:")
            print(f"  → {accounting_type['name']} (ID: {accounting_type['id']})")
            print()
            print("Next steps:")
            print(f"  1. Open and review: {output_file}")
            print("  2. Test with single voucher: python create_vouchers_for_ulp.py --create-single")
            print("  3. Create all vouchers: python create_vouchers_for_ulp.py --create-all")
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
            show_donation_type=False
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
        import json
        first_txn_raw = json.loads(ulp_transactions[0].get('raw_data', '{}'))
        check_account_id = first_txn_raw.get('checkAccount', {}).get('id')
        sev_client_id = first_txn_raw.get('sevClient', {}).get('id')
        
        # Determine which vouchers to create
        vouchers_to_create = [voucher_plan[0]] if args.create_single else voucher_plan
        
        print(f"Creating {len(vouchers_to_create)} voucher(s)...")
        print()
        
        created_vouchers = []
        failed_vouchers = []
        
        for i, plan in enumerate(vouchers_to_create, 1):
            print(f"[{i}/{len(vouchers_to_create)}] Creating voucher for transaction {plan['transaction_id']}...")
            print(f"    Amount: €{plan['amount']:,.2f}")
            print(f"    Payee: {plan['payee_payer_name']}")
            print(f"    Cost Centre: {plan['cost_centre']['name'] if plan['cost_centre'] else 'None'}")
            
            try:
                response = create_voucher_for_transaction(
                    client, plan, check_account_id, sev_client_id, is_income=False
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
                            date=plan['transaction_date'][:10]  # Use transaction date
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
                        status_name = {100: 'Open', 200: 'Linked', 300: 'Booked'}.get(new_status, f'Unknown ({new_status})')
                        
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

