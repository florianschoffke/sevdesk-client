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


def find_cost_centre_by_name(db: TransactionDB, payee_name: str, is_ulp_transaction: bool = False) -> dict:
    """
    Find a cost centre by payee name (case-insensitive).
    Special rule: For Tobias Zimmermann + ÜLP transaction, use "Tobias Zimmermann (ÜLP)"
    
    Args:
        db: Database connection
        payee_name: Name to search for
        is_ulp_transaction: Whether this is a ÜLP transaction
        
    Returns:
        Cost centre dict or None
    """
    if not payee_name:
        return None
    
    search_name = payee_name.lower().strip()
    all_cost_centres = db.get_all_cost_centres()
    
    # Special rule for Tobias Zimmermann with ÜLP
    if is_ulp_transaction and 'tobias zimmermann' in search_name:
        for cc in all_cost_centres:
            cc_name = cc.get('name', '').lower()
            if 'tobias zimmermann' in cc_name and 'ülp' in cc_name:
                return cc
    
    # Default: search for matching cost centre
    for cc in all_cost_centres:
        cc_name = cc.get('name', '').lower().strip()
        if search_name in cc_name or cc_name in search_name:
            return cc
    
    return None


def find_contact_by_name(db: TransactionDB, payee_name: str) -> dict:
    """
    Find a contact (supplier) by payee name (case-insensitive).
    
    Args:
        db: Database connection
        payee_name: Name to search for
        
    Returns:
        Contact dict or None
    """
    if not payee_name:
        return None
    
    search_name = payee_name.lower().strip()
    all_contacts = db.get_all_contacts()
    
    # Search for matching contact by name
    for contact in all_contacts:
        contact_name = contact.get('name', '')
        if not contact_name:
            continue
        contact_name = contact_name.lower().strip()
        
        # Try exact match first
        if search_name == contact_name:
            return contact
        
        # Try partial match (either direction)
        if search_name in contact_name or contact_name in search_name:
            return contact
    
    return None


def generate_voucher_number(transaction_id: str) -> str:
    """
    Generate a voucher number in format: BEL-YYYY-MM-DD--TRANSACTION_ID
    
    Args:
        transaction_id: The transaction ID
        
    Returns:
        Voucher number string
    """
    today = datetime.now().strftime('%Y-%m-%d')
    return f"BEL-{today}--{transaction_id}"


def create_voucher_for_transaction(client: SevDeskClient, plan: dict, check_account_id: str, sev_client_id: str) -> dict:
    """
    Create a voucher for a single transaction.
    
    Args:
        client: SevDesk API client
        plan: Voucher plan dictionary
        check_account_id: The check account ID for the transaction
        sev_client_id: The sevClient ID
        
    Returns:
        API response dictionary
    """
    import json
    
    # Build voucher data according to sevDesk API format
    amount = abs(float(plan['amount']))
    
    # Get transaction details for comment
    purpose = plan.get('payment_purpose', '') or ''  # Verwendungszweck
    
    voucher_data = {
        'voucher': {
            'objectName': 'Voucher',
            'mapAll': True,
            'voucherDate': plan['transaction_date'][:10],
            'supplierName': plan['payee_payer_name'],  # Set supplier name
            'description': plan['voucher_number'],  # Use voucher number as description
            'payDate': plan['transaction_date'][:10],
            'paymentDeadline': plan['transaction_date'][:10],  # Add Fälligkeit
            'status': 100,  # Open/Unpaid so we can book it
            'taxType': 'ss',  # Changed from 'default' to 'ss'
            'creditDebit': 'C',  # Changed from 'D' to 'C' for expenses (Credit)
            'voucherType': 'VOU',
            'currency': 'EUR',
            'sevClient': {
                'id': sev_client_id,
                'objectName': 'SevClient'
            }
        },
        'voucherPosSave': [
            {
                'objectName': 'VoucherPos',
                'mapAll': True,
                'accountingType': {
                    'id': str(plan['accounting_type']['id']),
                    'objectName': 'AccountingType'
                },
                'taxRate': 0,
                'sumNet': amount,
                'sumTax': 0,
                'sumGross': amount,
                'comment': purpose,  # Add comment with Verwendungszweck
            }
        ]
    }
    
    # Add supplier (contact) if available
    if plan.get('contact'):
        voucher_data['voucher']['supplier'] = {
            'id': plan['contact']['id'],
            'objectName': 'Contact'
        }
    
    # Add cost centre on both voucher and position level
    if plan['cost_centre']:
        # On voucher level
        voucher_data['voucher']['costCentre'] = {
            'id': plan['cost_centre']['id'],
            'objectName': 'CostCentre'
        }
        # Also on position level (keep for compatibility)
        voucher_data['voucherPosSave'][0]['costCentre'] = {
            'id': plan['cost_centre']['id'],
            'objectName': 'CostCentre'
        }
    
    # Create the voucher
    response = client.create_voucher(voucher_data)
    return response


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
            if 'ÜLP' in payment_purpose or 'Übungsleiterpauschale' in payment_purpose.lower():
                ulp_transactions.append(txn)
        
        print(f"✓ Found {len(ulp_transactions)} transactions matching 'ÜLP' or 'Übungsleiterpauschale'")
        print()
        
        if not ulp_transactions:
            print("No matching transactions found. Exiting.")
            return
        
        # Build voucher plan
        voucher_plan = []
        for txn in ulp_transactions:
            # Parse raw data to get payeePayerName
            import json
            raw_data = json.loads(txn.get('raw_data', '{}'))
            payee_payer_name = raw_data.get('payeePayerName', 'Unknown')
            
            # Check if this is a ÜLP transaction
            payment_purpose = txn.get('paymt_purpose', '') or ''
            is_ulp = 'ÜLP' in payment_purpose
            
            # Find matching cost centre (with special rule for Tobias + ÜLP)
            cost_centre = find_cost_centre_by_name(db, payee_payer_name, is_ulp_transaction=is_ulp)
            
            # Find matching contact (supplier)
            contact = find_contact_by_name(db, payee_payer_name)
            
            # Generate voucher number
            voucher_number = generate_voucher_number(txn['id'])
            
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
        
        # Build markdown content
        markdown_lines = []
        markdown_lines.append("# ÜLP Voucher Plan")
        markdown_lines.append("")
        markdown_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        markdown_lines.append(f"**Total Vouchers:** {len(voucher_plan)}")
        markdown_lines.append("")
        markdown_lines.append("## Vouchers to Create")
        markdown_lines.append("")
        markdown_lines.append("| Transaction ID | Date | Amount | Payee/Payer | Cost Centre | Voucher Number |")
        markdown_lines.append("|----------------|------|--------|-------------|-------------|----------------|")
        
        for plan in voucher_plan:
            cost_centre_name = plan['cost_centre']['name'] if plan['cost_centre'] else '❌ NOT FOUND'
            cost_centre_display = f"✅ {cost_centre_name}" if plan['cost_centre'] else cost_centre_name
            
            markdown_lines.append(
                f"| {plan['transaction_id']} | {plan['transaction_date'][:10]} | €{plan['amount']:,.2f} | "
                f"{plan['payee_payer_name']} | {cost_centre_display} | {plan['voucher_number']} |"
            )
        
        markdown_lines.append("")
        
        # Check for missing cost centres
        missing_cost_centres = [p for p in voucher_plan if not p['cost_centre']]
        if missing_cost_centres:
            markdown_lines.append("## ⚠️ Warnings")
            markdown_lines.append("")
            markdown_lines.append("**Transactions with no matching cost centre:**")
            markdown_lines.append("")
            for p in missing_cost_centres:
                markdown_lines.append(f"- {p['payee_payer_name']} (Transaction: {p['transaction_id']})")
            markdown_lines.append("")
            markdown_lines.append("*These vouchers will be created WITHOUT a cost centre assignment.*")
            markdown_lines.append("")
        
        # Add summary
        markdown_lines.append("## Configuration")
        markdown_lines.append("")
        markdown_lines.append(f"**Accounting Type:** {accounting_type['name']} (ID: {accounting_type['id']})")
        markdown_lines.append("")
        markdown_lines.append("## Next Steps")
        markdown_lines.append("")
        markdown_lines.append("1. Review the table above")
        markdown_lines.append("2. Verify cost centre assignments")
        markdown_lines.append("3. Run the script again with `--create-single` or `--create-all` flag to create vouchers")
        
        # Write to file
        output_file = "voucher_plan.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_lines))
        
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
            
            if missing_cost_centres:
                print(f"⚠️  WARNING: {len(missing_cost_centres)} transaction(s) have no matching cost centre")
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
        
        # Display the plan in a table format
        print("Vouchers to be created:")
        print()
        print(f"{'#':<4} {'Transaction ID':<15} {'Date':<12} {'Amount':<12} {'Payee/Payer':<30} {'Cost Centre':<25}")
        print("-" * 110)
        
        for i, plan in enumerate(voucher_plan if args.create_all else [voucher_plan[0]], 1):
            cost_centre_name = plan['cost_centre']['name'] if plan['cost_centre'] else '❌ NOT FOUND'
            print(f"{i:<4} {plan['transaction_id']:<15} {plan['transaction_date'][:10]:<12} €{plan['amount']:>9,.2f} {plan['payee_payer_name']:<30.30} {cost_centre_name:<25.25}")
        
        print()
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
        
        # Initialize API client
        print(f"Connecting to SevDesk API at {api_url}...")
        client = SevDeskClient(api_key=api_key, base_url=api_url)
        print("✓ Connected")
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
                response = create_voucher_for_transaction(client, plan, check_account_id, sev_client_id)
                
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

