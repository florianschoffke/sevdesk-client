#!/usr/bin/env python3
"""
Create vouchers for Spenden (Donations) transactions.

This script finds open incoming transactions (amount > 0) containing "Spende" 
in the payment purpose and creates vouchers for them.

Two types of donations:
1. Mission donations: purpose contains "Mission" or "Missionar" 
   → Cost Centre: "Spendeneingänge Missionare"
2. General donations: purpose contains only "Spende"
   → Cost Centre: "Spende        for plan in voucher_plan:
            # Icons: 🎯=mission, 🔄=jeske, 👤=tobias, 💝=general
            if plan['donation_type']        for i, plan in enumerate(voucher_plan if args.create_all else [voucher_plan[0]], 1):
            contact_status = "✅" if plan['contact'] else "❌"
            # Icons: 🎯=mission, 🔄=jeske, 👤=tobias, 💝=general
            if plan['donation_type'] == 'mission':
                type_icon = "🎯"
            elif plan['donation_type'] == 'jeske':
                type_icon = "🔄"
            elif plan['donation_type'] == 'tobias':
                type_icon = "👤"
            else:
                type_icon = "💝"
            
            purpose = (plan['payment_purpose'] or '')[:32]
            if len(plan['payment_purpose'] or '') > 32:
                purpose += '...'
            print(f"{i:<4} {plan['transaction_id']:<15} {plan['transaction_date'][:10]:<12} €{plan['amount']:>9,.2f} {plan['payee_payer_name']:<30.30} {purpose:<35.35} {type_icon} {plan['donation_type']:<7} {contact_status}")ssion':
                donation_type_icon = "🎯"
            elif plan['donation_type'] == 'jeske':
                donation_type_icon = "🔄"
            elif plan['donation_type'] == 'tobias':
                donation_type_icon = "👤"
            else:
                donation_type_icon = "💝"
            
            cost_centre_name = plan['cost_centre']['name']
            contact_status = f"✅ {plan['contact']['name']}" if plan['contact'] else '❌ NOT FOUND'
            # Truncate purpose to max 40 chars for readability
            purpose = (plan['payment_purpose'] or '')[:40]
            if len(plan['payment_purpose'] or '') > 40:
                purpose += '...'
            
            markdown_lines.append(
                f"| {plan['transaction_id']} | {plan['transaction_date'][:10]} | €{plan['amount']:,.2f} | "
                f"{plan['payee_payer_name']} | {purpose} | {donation_type_icon} {plan['donation_type']} | {cost_centre_name} | "
                f"{contact_status} | {plan['voucher_number']} |"
            )o"
   
Both use Accounting Type: "Spendeneingang"
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sevdesk.client import SevDeskClient
from database.db import TransactionDB
from reload_data import reload_all_data


def find_cost_centre_by_name(db: TransactionDB, name: str) -> dict:
    """
    Find a cost centre by exact name match.
    
    Args:
        db: Database connection
        name: Exact name to search for
        
    Returns:
        Cost centre dict or None
    """
    if not name:
        return None
    
    all_cost_centres = db.get_all_cost_centres()
    
    for cc in all_cost_centres:
        if cc.get('name') == name:
            return cc
    
    return None


def find_contact_by_name(db: TransactionDB, payee_name: str) -> dict:
    """
    Find a contact (donor) by payee name (case-insensitive).
    For donations, prioritize customers (category_id: 2) over suppliers (category_id: 3).
    When multiple names are present (e.g., "THOMAS HOCHSTETTER NINA HOCHSTETTER"),
    try matching the first name first.
    
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
    
    # For multi-name payees (e.g., "THOMAS HOCHSTETTER NINA HOCHSTETTER"),
    # try to extract individual full names by looking for repeated last names
    # or trying the first half of the words
    if len(search_words_list) >= 4:
        # Try first half (e.g., "THOMAS HOCHSTETTER" from "THOMAS HOCHSTETTER NINA HOCHSTETTER")
        mid_point = len(search_words_list) // 2
        first_half = ' '.join(search_words_list[:mid_point])
        search_alternatives.insert(0, first_half)  # Insert at beginning for priority
    
    # Also try matching "First Name + Last Word" for patterns like "Adrian und Diane Schmeichel"
    # where we want to match "Adrian Schmeichel"
    if len(search_words_list) >= 3 and 'und' in search_words_list:
        # Find position of 'und'
        und_idx = search_words_list.index('und')
        if und_idx > 0 and und_idx < len(search_words_list) - 1:
            # Take first name + last word (likely the surname)
            first_name = search_words_list[0]
            last_name = search_words_list[-1]
            first_person = f"{first_name} {last_name}"
            search_alternatives.insert(0, first_person)  # Highest priority
    
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
                # Exact match - prioritize customers (category 2)
                priority = 1000 - i  # Earlier alternatives have higher priority
                if category_id == 2:  # Customer
                    priority += 10000
                candidate_matches.append((priority, contact))
                break
        
        if candidate_matches and candidate_matches[-1][1] == contact:
            continue  # Already added as exact match
        
        # Try partial match (either direction) with any search alternative
        for i, search_alt in enumerate(search_alternatives):
            if search_alt in contact_normalized or contact_normalized in search_alt:
                priority = 500 - i  # Lower than exact match
                if category_id == 2:  # Customer
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
            # of the first words match (to avoid matching "Stefanie X" with "Matthias X")
            if len(search_words) >= 2 and len(contact_words) >= 2:
                # Get actual first words from normalized strings
                search_parts = search_normalized.split()
                contact_parts = contact_normalized.split()
                
                # If last names match but no first names match, penalize
                if common_words and search_parts[0] not in contact_parts and contact_parts[0] not in search_parts:
                    # Only the last name matches - this is not a good match
                    score = 0
            
            if score > 0:
                # Prefer customers (category 2) for donations
                priority = score
                if category_id == 2:  # Customer
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


def determine_donation_type(payment_purpose: str) -> str:
    """
    Determine the type of donation based on payment purpose.
    
    Args:
        payment_purpose: Payment purpose text
        
    Returns:
        'mission' or 'general'
    """
    if not payment_purpose:
        return 'general'
    
    purpose_lower = payment_purpose.lower()
    
    # Check for mission-related keywords
    if 'mission' in purpose_lower or 'missionar' in purpose_lower:
        return 'mission'
    
    return 'general'


def create_voucher_for_transaction(client: SevDeskClient, plan: dict, 
                                   check_account_id: str, sev_client_id: str) -> dict:
    """
    Create a voucher for a donation transaction.
    
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
    # For income (donations): amount is positive, creditDebit is 'D'
    amount = abs(float(plan['amount']))
    
    # Get transaction details for comment
    purpose = plan.get('payment_purpose', '') or ''  # Verwendungszweck
    
    voucher_data = {
        'voucher': {
            'objectName': 'Voucher',
            'mapAll': True,
            'voucherDate': plan['transaction_date'][:10],
            'description': plan['voucher_number'],  # Use voucher number as description
            'payDate': plan['transaction_date'][:10],
            'deliveryDate': plan['transaction_date'][:10],  # Add Lieferdatum
            'paymentDeadline': plan['transaction_date'][:10],  # Add Fälligkeit
            'status': 100,  # Open/Unpaid so we can book it (will change to 1000 after booking)
            'taxType': 'ss',  # Tax type
            'creditDebit': 'D',  # Debit for income vouchers
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
                'sumNet': amount,  # Positive for income
                'sumTax': 0,
                'sumGross': amount,  # Positive for income
                'comment': purpose,  # Add comment with Verwendungszweck
            }
        ]
    }
    
    # Add supplier (contact) if available - IMPORTANT for donations!
    # Only use supplierName as fallback if no contact is linked
    if plan.get('contact'):
        voucher_data['voucher']['supplier'] = {
            'id': plan['contact']['id'],
            'objectName': 'Contact'
        }
    else:
        # Only set supplierName if no contact is available
        voucher_data['voucher']['supplierName'] = plan['payee_payer_name']
    
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
    
    parser = argparse.ArgumentParser(description='Create vouchers for Spenden (donation) transactions')
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
    
    # Initialize database
    print(f"Opening database: {db_path}")
    with TransactionDB(db_path=db_path) as db:
        # Get accounting type for Spendeneingang
        accounting_type = None
        all_accounting_types = db.get_all_accounting_types()
        for at in all_accounting_types:
            if at.get('name') == 'Spendeneingang':
                accounting_type = at
                break
        
        if not accounting_type:
            print("Error: Could not find 'Spendeneingang' accounting type!")
            sys.exit(1)
        
        print(f"✓ Found accounting type: {accounting_type['name']} (ID: {accounting_type['id']})")
        print()
        
        # Get cost centres
        mission_cost_centre = find_cost_centre_by_name(db, 'Spendeneingänge Missionare')
        general_cost_centre = find_cost_centre_by_name(db, 'Spendeneingänge Konto')
        jeske_cost_centre = find_cost_centre_by_name(db, 'Jeske (Durchlaufende Posten)')
        tobias_cost_centre = find_cost_centre_by_name(db, 'Tobias Zimmermann (Spende für Tobias)')
        
        if not mission_cost_centre or not general_cost_centre or not jeske_cost_centre or not tobias_cost_centre:
            print("Error: Could not find required cost centres!")
            if not mission_cost_centre:
                print("  Missing: Spendeneingänge Missionare")
            if not general_cost_centre:
                print("  Missing: Spendeneingänge Konto")
            if not jeske_cost_centre:
                print("  Missing: Jeske (Durchlaufende Posten)")
            if not tobias_cost_centre:
                print("  Missing: Tobias Zimmermann (Spende für Tobias)")
            sys.exit(1)
        
        print(f"✓ Found cost centre (Mission): {mission_cost_centre['name']} (ID: {mission_cost_centre['id']})")
        print(f"✓ Found cost centre (General): {general_cost_centre['name']} (ID: {general_cost_centre['id']})")
        print(f"✓ Found cost centre (Jeske): {jeske_cost_centre['name']} (ID: {jeske_cost_centre['id']})")
        print(f"✓ Found cost centre (Tobias): {tobias_cost_centre['name']} (ID: {tobias_cost_centre['id']})")
        print()
        
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
            
            # Must be income (positive) and contain "Spende"
            if amount > 0 and 'Spende' in payment_purpose:
                spenden_transactions.append(txn)
        
        print(f"✓ Found {len(spenden_transactions)} donation transactions (income with 'Spende')")
        print()
        
        if not spenden_transactions:
            print("No matching transactions found. Exiting.")
            return
        
        # Build voucher plan
        voucher_plan = []
        for txn in spenden_transactions:
            # Parse raw data to get payeePayerName
            import json
            raw_data = json.loads(txn.get('raw_data', '{}'))
            payee_payer_name = raw_data.get('payeePayerName', 'Unknown')
            
            # Determine donation type
            donation_type = determine_donation_type(txn.get('paymt_purpose'))
            
            # Select appropriate cost centre
            payment_purpose = txn.get('paymt_purpose', '') or ''
            
            # Special rules for specific donation purposes
            if 'Artur Jeske' in payment_purpose:
                # Donations for Artur Jeske → Jeske (Durchlaufende Posten)
                cost_centre = jeske_cost_centre
                donation_type = 'jeske'
            elif 'Spende Tobias Zimmermann' in payment_purpose:
                # Donations for Tobias Zimmermann → Tobias Zimmermann (Spende für Tobias)
                cost_centre = tobias_cost_centre
                donation_type = 'tobias'
            elif donation_type == 'mission':
                cost_centre = mission_cost_centre
            else:
                cost_centre = general_cost_centre
            
            # Find matching contact (donor) - IMPORTANT!
            contact = find_contact_by_name(db, payee_payer_name)
            
            # Generate voucher number
            voucher_number = generate_voucher_number(txn['id'])
            
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
        
        # Build markdown content
        markdown_lines = []
        markdown_lines.append("# Spenden Voucher Plan")
        markdown_lines.append("")
        markdown_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        markdown_lines.append(f"**Total Vouchers:** {len(voucher_plan)}")
        markdown_lines.append("")
        markdown_lines.append("## Vouchers to Create")
        markdown_lines.append("")
        markdown_lines.append("| Transaction ID | Date | Amount | Donor | Purpose | Type | Cost Centre | Contact | Voucher Number |")
        markdown_lines.append("|----------------|------|--------|-------|---------|------|-------------|---------|----------------|")
        
        for plan in voucher_plan:
            donation_type_icon = "🎯" if plan['donation_type'] == 'mission' else "�" if plan['donation_type'] == 'jeske' else "�💝"
            cost_centre_name = plan['cost_centre']['name']
            contact_status = f"✅ {plan['contact']['name']}" if plan['contact'] else '❌ NOT FOUND'
            # Truncate purpose to max 40 chars for readability
            purpose = (plan['payment_purpose'] or '')[:40]
            if len(plan['payment_purpose'] or '') > 40:
                purpose += '...'
            
            markdown_lines.append(
                f"| {plan['transaction_id']} | {plan['transaction_date'][:10]} | €{plan['amount']:,.2f} | "
                f"{plan['payee_payer_name']} | {purpose} | {donation_type_icon} {plan['donation_type']} | {cost_centre_name} | "
                f"{contact_status} | {plan['voucher_number']} |"
            )
        
        markdown_lines.append("")
        
        # Check for missing contacts - CRITICAL for donations!
        missing_contacts = [p for p in voucher_plan if not p['contact']]
        if missing_contacts:
            markdown_lines.append("## ⚠️ CRITICAL WARNINGS")
            markdown_lines.append("")
            markdown_lines.append("**Transactions with no matching contact (donor):**")
            markdown_lines.append("")
            for p in missing_contacts:
                markdown_lines.append(f"- {p['payee_payer_name']} (Transaction: {p['transaction_id']})")
            markdown_lines.append("")
            markdown_lines.append("*These vouchers will be created WITHOUT a contact/donor assignment.*")
            markdown_lines.append("*This is NOT recommended for donation tracking!*")
            markdown_lines.append("")
        
        # Statistics
        mission_count = len([p for p in voucher_plan if p['donation_type'] == 'mission'])
        general_count = len([p for p in voucher_plan if p['donation_type'] == 'general'])
        jeske_count = len([p for p in voucher_plan if p['donation_type'] == 'jeske'])
        tobias_count = len([p for p in voucher_plan if p['donation_type'] == 'tobias'])
        
        markdown_lines.append("## Statistics")
        markdown_lines.append("")
        markdown_lines.append(f"- **Mission Donations:** {mission_count}")
        markdown_lines.append(f"- **General Donations:** {general_count}")
        markdown_lines.append(f"- **Jeske (Pass-through) Donations:** {jeske_count}")
        markdown_lines.append(f"- **Tobias Zimmermann Donations:** {tobias_count}")
        markdown_lines.append(f"- **Total Donations:** {len(voucher_plan)}")
        markdown_lines.append(f"- **Missing Contacts:** {len(missing_contacts)}")
        markdown_lines.append("")
        
        # Add summary
        markdown_lines.append("## Configuration")
        markdown_lines.append("")
        markdown_lines.append(f"**Accounting Type:** {accounting_type['name']} (ID: {accounting_type['id']})")
        markdown_lines.append(f"**Cost Centre (Mission):** {mission_cost_centre['name']} (ID: {mission_cost_centre['id']})")
        markdown_lines.append(f"**Cost Centre (General):** {general_cost_centre['name']} (ID: {general_cost_centre['id']})")
        markdown_lines.append(f"**Cost Centre (Jeske):** {jeske_cost_centre['name']} (ID: {jeske_cost_centre['id']})")
        markdown_lines.append(f"**Cost Centre (Tobias):** {tobias_cost_centre['name']} (ID: {tobias_cost_centre['id']})")
        markdown_lines.append("")
        markdown_lines.append("## Next Steps")
        markdown_lines.append("")
        markdown_lines.append("1. Review the table above")
        markdown_lines.append("2. **IMPORTANT:** Verify all donors have matching contacts!")
        markdown_lines.append("3. Run the script again with `--create-single` or `--create-all` flag to create vouchers")
        
        # Write to file
        output_file = "voucher_plan_spenden.md"
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
            print(f"  - Mission donations: {mission_count}")
            print(f"  - General donations: {general_count}")
            print(f"  - Jeske (pass-through) donations: {jeske_count}")
            print(f"  - Tobias Zimmermann donations: {tobias_count}")
            print()
            
            if missing_contacts:
                print(f"⚠️  CRITICAL: {len(missing_contacts)} transaction(s) have no matching contact!")
                print("   Donation tracking requires contact assignment!")
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
        
        # Display the plan in a table format
        print("Vouchers to be created:")
        print()
        print(f"{'#':<4} {'Transaction ID':<15} {'Date':<12} {'Amount':<12} {'Donor':<30} {'Purpose':<35} {'Type':<10} {'Contact':<15}")
        print("-" * 145)
        
        for i, plan in enumerate(voucher_plan if args.create_all else [voucher_plan[0]], 1):
            contact_status = "✅" if plan['contact'] else "❌"
            type_icon = "🎯" if plan['donation_type'] == 'mission' else "�" if plan['donation_type'] == 'jeske' else "�💝"
            purpose = (plan['payment_purpose'] or '')[:32]
            if len(plan['payment_purpose'] or '') > 32:
                purpose += '...'
            print(f"{i:<4} {plan['transaction_id']:<15} {plan['transaction_date'][:10]:<12} €{plan['amount']:>9,.2f} {plan['payee_payer_name']:<30.30} {purpose:<35.35} {type_icon} {plan['donation_type']:<7} {contact_status}")
        
        print()
        print(f"Total: {len(voucher_plan) if args.create_all else 1} voucher(s) will be created")
        print()
        
        if missing_contacts:
            print("⚠️  CRITICAL WARNING: Some transactions have no matching contact!")
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
            print(f"[{i}/{len(vouchers_to_create)}] Creating voucher for transaction {plan['transaction_id']}...")
            print(f"    Amount: €{plan['amount']:,.2f}")
            print(f"    Donor: {plan['payee_payer_name']}")
            print(f"    Type: {plan['donation_type']}")
            print(f"    Cost Centre: {plan['cost_centre']['name']}")
            print(f"    Contact: {plan['contact']['name'] if plan['contact'] else '❌ None'}")
            
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
                            date=plan['transaction_date'][:10],  # Use transaction date
                            is_income=True  # Donations are income vouchers
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
