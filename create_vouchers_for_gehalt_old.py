#!/usr/bin/env python3
"""
Create vouchers for Gehalt (Salary) transactions.

This script finds open transactions containing "Gehalt" in the payment purpose
and creates vouchers for them.
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sevdesk.client import SevDeskClient
from database.db import TransactionDB
from reload_data import reload_all_data


def find_cost_centre_by_name(db: TransactionDB, payee_name: str) -> dict:
    """
    Find a cost centre by payee name (case-insensitive).
    Special mapping rules for specific names.
    
    Args:
        db: Database connection
        payee_name: Name to search for
        
    Returns:
        Cost centre dict or None
    """
    if not payee_name:
        return None
    
    search_name = payee_name.lower().strip()
    all_cost_centres = db.get_all_cost_centres()
    
    # Special mapping rule for GWENDOLYN RUTH DEWHURST -> Gwen Dewhurst
    if 'gwendolyn' in search_name and 'dewhurst' in search_name:
        for cc in all_cost_centres:
            cc_name = cc.get('name', '').lower()
            if cc_name == 'gwen dewhurst':
                return cc
    
    # Special mapping rule for Samuel JeanRichard-dit-Bressel -> Samuel Jeanrichard (intern)
    if 'samuel' in search_name and ('jeanrichard' in search_name or 'jean' in search_name):
        for cc in all_cost_centres:
            cc_name = cc.get('name', '').lower()
            if 'samuel jeanrichard' in cc_name and 'intern' in cc_name:
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
    For expenses, prioritize suppliers (category_id: 3) over customers (category_id: 2).
    Uses advanced fuzzy matching with Unicode normalization.
    
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
    
    # Normalize names for better matching
    def normalize_name(name):
        """Normalize name by removing punctuation and extra spaces."""
        import re
        import unicodedata
        # Normalize unicode (e.g., ß → ss)
        name = unicodedata.normalize('NFKD', name)
        # Remove diacritics
        name = ''.join([c for c in name if not unicodedata.combining(c)])
        # Replace ß with ss
        name = name.replace('ß', 'ss').replace('ẞ', 'SS')
        # Remove commas, dots, and extra spaces
        name = re.sub(r'[,.]', ' ', name)
        # Normalize whitespace
        name = ' '.join(name.split())
        return name.lower()
    
    search_normalized = normalize_name(search_name)
    search_words_list = search_normalized.split()
    search_words = set(search_words_list)
    
    # Handle "lastname, firstname" format by reversing
    search_alternatives = [search_normalized]
    if ',' in payee_name:
        parts = [p.strip() for p in payee_name.split(',')]
        if len(parts) == 2:
            reversed_name = f"{parts[1]} {parts[0]}"
            search_alternatives.append(normalize_name(reversed_name))
    
    # Special mapping: GWENDOLYN RUTH DEWHURST → Gwen Dewhurst (prefer this over Gwendolyn)
    if 'gwendolyn' in search_normalized and 'dewhurst' in search_normalized:
        # Look specifically for "Gwen Dewhurst" (not "Gwendolyn Dewhurst")
        for contact in all_contacts:
            contact_name = contact.get('name', '').lower().strip()
            if contact_name == 'gwen dewhurst':
                # Return this contact regardless of category
                return contact
    
    # Search for matching contact by name
    candidate_matches = []
    
    for contact in all_contacts:
        contact_name = contact.get('name', '')
        if not contact_name:
            continue
        
        contact_name_lower = contact_name.lower().strip()
        contact_normalized = normalize_name(contact_name)
        contact_words = set(contact_normalized.split())
        category_id = contact.get('category', {}).get('id') if isinstance(contact.get('category'), dict) else contact.get('category_id')
        
        # Try exact match first with any search alternative
        for i, search_alt in enumerate(search_alternatives):
            if search_alt == contact_normalized:
                # Exact match - prioritize suppliers (category 3) for expenses
                priority = 1000 - i  # Earlier alternatives have higher priority
                if category_id == 3:  # Supplier
                    priority += 10000
                candidate_matches.append((priority, contact))
                break
        
        if candidate_matches and candidate_matches[-1][1] == contact:
            continue  # Already added as exact match
        
        # Try partial match (either direction) with any search alternative
        for i, search_alt in enumerate(search_alternatives):
            if search_alt in contact_normalized or contact_normalized in search_alt:
                priority = 500 - i  # Lower than exact match
                if category_id == 3:  # Supplier
                    priority += 10000
                candidate_matches.append((priority, contact))
                break
        
        if candidate_matches and candidate_matches[-1][1] == contact:
            continue  # Already added as partial match
        
        # Calculate word overlap score for fuzzy matching
        if search_words and contact_words:
            common_words = search_words & contact_words
            # Score based on how many words match
            score = len(common_words)
            
            # Bonus if all contact words are in search words
            if contact_words.issubset(search_words):
                score += 10
            
            # Additional check: if both have 2+ words, require that at least one 
            # of the first words match
            if len(search_words) >= 2 and len(contact_words) >= 2:
                # Get actual first words from normalized strings
                search_parts = search_normalized.split()
                contact_parts = contact_normalized.split()
                
                # If last names match but no first names match, penalize
                if common_words and search_parts[0] not in contact_parts and contact_parts[0] not in search_parts:
                    # Only the last name matches - this is not a good match
                    score = 0
            
            if score > 0:
                # Prefer suppliers (category 3) for expenses
                priority = score
                if category_id == 3:  # Supplier
                    priority += 10000
                candidate_matches.append((priority, contact))
    
    # Return best match (highest priority)
    if candidate_matches:
        candidate_matches.sort(key=lambda x: x[0], reverse=True)
        return candidate_matches[0][1]
    
    return None


def generate_voucher_number(transaction_id: str) -> str:
    """
    Generate a voucher number based on transaction ID.
    Format: BEL-YYYY-MM-DD-TRANSACTION_ID
    
    Args:
        transaction_id: Transaction ID
        
    Returns:
        Voucher number string
    """
    today = datetime.now().strftime('%Y-%m-%d')
    return f"BEL-{today}-{transaction_id}"


def create_voucher_for_transaction(client: SevDeskClient, plan: dict, 
                                   check_account_id: str, sev_client_id: str) -> dict:
    """
    Create a voucher for a Gehalt transaction.
    
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
            'supplierName': plan['payee_payer_name'],  # Set supplier name as fallback
            'description': plan['voucher_number'],  # Use voucher number as description
            'payDate': plan['transaction_date'][:10],
            'paymentDeadline': plan['transaction_date'][:10],  # Add Fälligkeit
            'status': 100,  # Open/Unpaid so we can book it
            'taxType': 'ss',  # Tax type
            'creditDebit': 'C',  # Credit for expenses
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Create vouchers for Gehalt transactions')
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
    print("Gehalt Voucher Creator")
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
        # Get accounting type for Lohn / Gehalt
        accounting_type = None
        all_accounting_types = db.get_all_accounting_types()
        for at in all_accounting_types:
            if 'Lohn' in at.get('name', '') and 'Gehalt' in at.get('name', ''):
                accounting_type = at
                break
        
        if not accounting_type:
            print("Error: Could not find 'Lohn / Gehalt' accounting type!")
            print("\nSearching for similar accounting types...")
            for at in all_accounting_types:
                name = at.get('name', '').lower()
                if 'lohn' in name or 'gehalt' in name:
                    print(f"  - {at.get('name')} (ID: {at.get('id')})")
            sys.exit(1)
        
        print(f"✓ Found accounting type: {accounting_type['name']} (ID: {accounting_type['id']})")
        print()
        
        # Get all open transactions
        print("Fetching open transactions...")
        all_transactions = db.get_all_transactions(status=100)
        print(f"✓ Found {len(all_transactions)} open transactions")
        print()
        
        # Filter transactions with Gehalt (case-insensitive)
        gehalt_transactions = []
        for txn in all_transactions:
            payment_purpose = txn.get('paymt_purpose', '') or ''
            payment_purpose_lower = payment_purpose.lower()
            if 'gehalt' in payment_purpose_lower:
                gehalt_transactions.append(txn)
        
        print(f"✓ Found {len(gehalt_transactions)} transactions matching 'Gehalt'")
        print()
        
        if not gehalt_transactions:
            print("No matching transactions found. Exiting.")
            return
        
        # Build voucher plan
        voucher_plan = []
        for txn in gehalt_transactions:
            # Parse raw data to get payeePayerName
            import json
            raw_data = json.loads(txn.get('raw_data', '{}'))
            payee_payer_name = raw_data.get('payeePayerName', 'Unknown')
            
            # Find matching cost centre
            cost_centre = find_cost_centre_by_name(db, payee_payer_name)
            
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
        markdown_lines.append("# Gehalt Voucher Plan")
        markdown_lines.append("")
        markdown_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        markdown_lines.append(f"**Total Vouchers:** {len(voucher_plan)}")
        markdown_lines.append("")
        markdown_lines.append("## Vouchers to Create")
        markdown_lines.append("")
        markdown_lines.append("| Transaction ID | Date | Amount | Payee/Payer | Cost Centre | Contact | Voucher Number |")
        markdown_lines.append("|----------------|------|--------|-------------|-------------|---------|----------------|")
        
        for plan in voucher_plan:
            cost_centre_name = plan['cost_centre']['name'] if plan['cost_centre'] else '❌ NOT FOUND'
            cost_centre_display = f"✅ {cost_centre_name}" if plan['cost_centre'] else cost_centre_name
            
            contact_name = plan['contact']['name'] if plan['contact'] else '❌ NOT FOUND'
            contact_display = f"✅ {contact_name}" if plan['contact'] else contact_name
            
            markdown_lines.append(
                f"| {plan['transaction_id']} | {plan['transaction_date'][:10]} | €{plan['amount']:,.2f} | "
                f"{plan['payee_payer_name']} | {cost_centre_display} | {contact_display} | {plan['voucher_number']} |"
            )
        
        markdown_lines.append("")
        
        # Check for missing cost centres and contacts
        missing_cost_centres = [p for p in voucher_plan if not p['cost_centre']]
        missing_contacts = [p for p in voucher_plan if not p['contact']]
        
        if missing_cost_centres or missing_contacts:
            markdown_lines.append("## ⚠️ Warnings")
            markdown_lines.append("")
            
            if missing_cost_centres:
                markdown_lines.append("**Transactions with no matching cost centre:**")
                markdown_lines.append("")
                for p in missing_cost_centres:
                    markdown_lines.append(f"- {p['payee_payer_name']} (Transaction: {p['transaction_id']})")
                markdown_lines.append("")
                markdown_lines.append("*These vouchers will be created WITHOUT a cost centre assignment.*")
                markdown_lines.append("")
            
            if missing_contacts:
                markdown_lines.append("**Transactions with no matching contact:**")
                markdown_lines.append("")
                for p in missing_contacts:
                    markdown_lines.append(f"- {p['payee_payer_name']} (Transaction: {p['transaction_id']})")
                markdown_lines.append("")
                markdown_lines.append("*These vouchers will be created WITHOUT a contact/supplier link.*")
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
        output_file = "voucher_plan_gehalt.md"
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
            
            if missing_contacts:
                print(f"⚠️  WARNING: {len(missing_contacts)} transaction(s) have no matching contact")
                print("   See the markdown file for details.")
                print()
            
            print("Accounting Type for all positions:")
            print(f"  → {accounting_type['name']} (ID: {accounting_type['id']})")
            print()
            print("Next steps:")
            print(f"  1. Open and review: {output_file}")
            print("  2. Test with single voucher: python create_vouchers_for_gehalt.py --create-single")
            print("  3. Create all vouchers: python create_vouchers_for_gehalt.py --create-all")
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
        print(f"{'#':<4} {'Transaction ID':<15} {'Date':<12} {'Amount':<12} {'Payee/Payer':<25} {'Cost Centre':<25} {'Contact':<20}")
        print("-" * 125)
        
        for i, plan in enumerate(voucher_plan if args.create_all else [voucher_plan[0]], 1):
            cost_centre_name = plan['cost_centre']['name'] if plan['cost_centre'] else '❌ NOT FOUND'
            contact_name = plan['contact']['name'] if plan['contact'] else '❌ NOT FOUND'
            print(f"{i:<4} {plan['transaction_id']:<15} {plan['transaction_date'][:10]:<12} €{plan['amount']:>9,.2f} {plan['payee_payer_name']:<25.25} {cost_centre_name:<25.25} {contact_name:<20.20}")
        
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
        first_txn_raw = json.loads(gehalt_transactions[0].get('raw_data', '{}'))
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
        print("Verifying transaction statuses...")
        print()
        
        # Reload transactions from API
        print("Reloading transactions from API...")
        client_for_reload = SevDeskClient(api_key=api_key, base_url=api_url)
        all_fresh_transactions = client_for_reload.get_all_transactions()
        print(f"✓ Loaded {len(all_fresh_transactions)} transactions")
        print()
        
        # Check status changes
        for created in created_vouchers:
            txn_id = created['plan']['transaction_id']
            old_status = 100  # Was open before
            
            # Find the transaction in fresh data
            new_txn = next((t for t in all_fresh_transactions if t['id'] == txn_id), None)
            new_status = new_txn['status'] if new_txn else 'Not found'
            
            status_display = f"{old_status} → {new_status}"
            status_name = {100: 'Open', 200: 'Linked', 400: 'Paid'}.get(new_status, f'Unknown ({new_status})')
            
            print(f"✓ Transaction {txn_id}: {status_display} ({status_name})")
        
        print()
        print("Updating local database...")
        db.bulk_insert_transactions(all_fresh_transactions)
        print(f"✓ Updated {len(all_fresh_transactions)} transactions in database")
        print()
        
        print("=" * 80)
        print("DONE")
        print("=" * 80)


if __name__ == '__main__':
    main()
