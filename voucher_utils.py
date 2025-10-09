#!/usr/bin/env python3
"""
Shared utilities for voucher creation scripts.

This module provides common functions for generating voucher plans,
markdown tables, and other shared functionality across different
voucher types (ÜLP, Gehalt, Spenden).
"""
from datetime import datetime
from typing import List, Dict, Optional


def get_next_voucher_number(client) -> int:
    """
    Get the next voucher number by finding the last voucher with pattern B-YYYY-NR.
    
    Args:
        client: SevDeskClient instance for fetching vouchers
        
    Returns:
        The next number to use (as integer)
    """
    from datetime import datetime
    import re
    
    current_year = datetime.now().year
    
    try:
        # Fetch recent vouchers and search for B-YYYY-NR pattern
        vouchers = client.get_all_vouchers(limit=100, sort_by_date=True)
        
        highest_nr = 0
        for voucher in vouchers:
            # Check both voucherNumber and description fields
            voucher_number = voucher.get('voucherNumber', '') or voucher.get('description', '')
            
            # Try to parse format B-YYYY-NR
            match = re.match(r'B-(\d{4})-(\d+)', str(voucher_number))
            
            if match:
                year = int(match.group(1))
                nr = int(match.group(2))
                
                # Only consider vouchers from current year
                if year == current_year and nr > highest_nr:
                    highest_nr = nr
        
        # Return next number
        return highest_nr + 1
            
    except Exception as e:
        # On any error, fall back to 1
        print(f"⚠️  Warning: Could not fetch last voucher number: {e}")
        print(f"   Starting with B-{current_year}-1")
        return 1


def generate_voucher_numbers(client, count: int) -> list:
    """
    Generate a list of consecutive voucher numbers in format B-YYYY-NR.
    
    This function fetches the last voucher once and then generates
    consecutive numbers for all transactions.
    
    Args:
        client: SevDeskClient instance
        count: Number of voucher numbers to generate
        
    Returns:
        List of voucher number strings
    """
    from datetime import datetime
    
    current_year = datetime.now().year
    next_nr = get_next_voucher_number(client)
    
    # Generate consecutive numbers
    voucher_numbers = []
    for i in range(count):
        voucher_numbers.append(f"B-{current_year}-{next_nr + i}")
    
    return voucher_numbers


def build_voucher_plan_markdown(
    title: str,
    voucher_plan: List[Dict],
    accounting_type: Dict,
    extra_sections: Optional[List[str]] = None,
    show_donation_type: bool = False
) -> List[str]:
    """
    Build a standardized markdown document for voucher plans.
    
    Args:
        title: The title of the plan (e.g., "ÜLP Voucher Plan", "Spenden Voucher Plan")
        voucher_plan: List of voucher plan dictionaries
        accounting_type: The accounting type dictionary
        extra_sections: Optional list of extra markdown lines to insert before Configuration
        show_donation_type: Whether to show donation type column (for Spenden)
        
    Returns:
        List of markdown lines
    """
    markdown_lines = []
    
    # Header
    markdown_lines.append(f"# {title}")
    markdown_lines.append("")
    markdown_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    markdown_lines.append(f"**Total Vouchers:** {len(voucher_plan)}")
    markdown_lines.append("")
    
    # Table section
    markdown_lines.append("## Vouchers to Create")
    markdown_lines.append("")
    
    # Table header - conditional based on type
    if show_donation_type:
        markdown_lines.append("| Transaction ID | Date | Amount | Donor | Purpose | Type | Cost Centre | Contact | Belegkategorie | Voucher Number |")
        markdown_lines.append("|----------------|------|--------|-------|---------|------|-------------|---------|----------------|----------------|")
    else:
        markdown_lines.append("| Transaction ID | Date | Amount | Payee/Payer | Cost Centre | Contact | Belegkategorie | Voucher Number |")
        markdown_lines.append("|----------------|------|--------|-------------|-------------|---------|----------------|----------------|")
    
    # Table rows
    for plan in voucher_plan:
        cost_centre_name = plan['cost_centre']['name'] if plan['cost_centre'] else '❌ NOT FOUND'
        cost_centre_display = f"✅ {cost_centre_name}" if plan['cost_centre'] else cost_centre_name
        contact_display = f"✅ {plan['contact']['name']}" if plan['contact'] else '❌ NOT FOUND'
        accounting_type_name = plan.get('accounting_type', {}).get('name', 'N/A')
        
        if show_donation_type:
            # Donation type icon
            donation_type = plan.get('donation_type', 'general')
            if donation_type == 'mission':
                type_icon = "🎯"
            elif donation_type == 'jeske':
                type_icon = "🔄"
            elif donation_type == 'tobias':
                type_icon = "👤"
            else:
                type_icon = "💝"
            
            # Truncate purpose to max 40 chars
            purpose = (plan.get('payment_purpose', '') or '')[:40]
            if len(plan.get('payment_purpose', '') or '') > 40:
                purpose += '...'
            
            markdown_lines.append(
                f"| {plan['transaction_id']} | {plan['transaction_date'][:10]} | €{plan['amount']:,.2f} | "
                f"{plan['payee_payer_name']} | {purpose} | {type_icon} {donation_type} | {cost_centre_display} | "
                f"{contact_display} | {accounting_type_name} | {plan['voucher_number']} |"
            )
        else:
            markdown_lines.append(
                f"| {plan['transaction_id']} | {plan['transaction_date'][:10]} | €{plan['amount']:,.2f} | "
                f"{plan['payee_payer_name']} | {cost_centre_display} | {contact_display} | {accounting_type_name} | {plan['voucher_number']} |"
            )
    
    markdown_lines.append("")
    
    # Check for missing cost centres or contacts
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
            markdown_lines.append("*These vouchers will be created WITHOUT a supplier/customer link.*")
            markdown_lines.append("")
    
    # Extra sections (e.g., donation type statistics)
    if extra_sections:
        markdown_lines.extend(extra_sections)
    
    # Configuration
    markdown_lines.append("## Configuration")
    markdown_lines.append("")
    markdown_lines.append(f"**Accounting Type:** {accounting_type['name']} (ID: {accounting_type['id']})")
    markdown_lines.append("")
    
    # Statistics
    markdown_lines.append("## Statistics")
    markdown_lines.append("")
    markdown_lines.append(f"- **Total Vouchers:** {len(voucher_plan)}")
    markdown_lines.append(f"- **Missing Contacts:** {len(missing_contacts)}")
    markdown_lines.append(f"- **Missing Cost Centres:** {len(missing_cost_centres)}")
    markdown_lines.append("")
    
    # Next steps
    markdown_lines.append("## Next Steps")
    markdown_lines.append("")
    markdown_lines.append("1. Review the table above")
    markdown_lines.append("2. Verify cost centre and contact assignments")
    markdown_lines.append("3. Run the script again with `--create-single` or `--create-all` flag to create vouchers")
    
    return markdown_lines


def print_console_summary(
    title: str,
    output_file: str,
    voucher_count: int,
    accounting_type: Dict,
    missing_cost_centres: int = 0,
    missing_contacts: int = 0,
    script_name: str = "script.py"
):
    """
    Print a standardized console summary for voucher plans.
    
    Args:
        title: The title (e.g., "ÜLP Voucher Creator")
        output_file: The output markdown file path
        voucher_count: Total number of vouchers
        accounting_type: The accounting type dictionary
        missing_cost_centres: Number of transactions with missing cost centres
        missing_contacts: Number of transactions with missing contacts
        script_name: The script filename for the help text
    """
    print("=" * 80)
    print(f"{title} - PLAN GENERATED")
    print("=" * 80)
    print()
    print(f"✓ Plan saved to: {output_file}")
    print(f"✓ Total vouchers to create: {voucher_count}")
    print()
    
    if missing_cost_centres:
        print(f"⚠️  WARNING: {missing_cost_centres} transaction(s) have no matching cost centre")
        print("   See the markdown file for details.")
        print()
    
    if missing_contacts:
        print(f"⚠️  WARNING: {missing_contacts} transaction(s) have no matching contact")
        print("   See the markdown file for details.")
        print()
    
    print("Accounting Type for all positions:")
    print(f"  → {accounting_type['name']} (ID: {accounting_type['id']})")
    print()
    print("Next steps:")
    print(f"  1. Open and review: {output_file}")
    print(f"  2. Test with single voucher: python {script_name} --create-single")
    print(f"  3. Create all vouchers: python {script_name} --create-all")
    print()
    print("=" * 80)


def print_voucher_table(
    voucher_plan: List[Dict],
    create_all: bool = False,
    show_donation_type: bool = False
):
    """
    Print a console table of vouchers to be created.
    
    Args:
        voucher_plan: List of voucher plan dictionaries
        create_all: Whether to show all vouchers or just the first one
        show_donation_type: Whether to show donation type column (for Spenden)
    """
    print("Vouchers to be created:")
    print()
    
    if show_donation_type:
        print(f"{'#':<4} {'Transaction ID':<15} {'Date':<12} {'Amount':<12} {'Donor':<30} {'Type':<7} {'Contact'}")
        print("-" * 95)
        
        for i, plan in enumerate(voucher_plan if create_all else [voucher_plan[0]], 1):
            contact_status = "✅" if plan['contact'] else "❌"
            donation_type = plan.get('donation_type', 'general')
            if donation_type == 'mission':
                type_icon = "🎯"
            elif donation_type == 'jeske':
                type_icon = "🔄"
            elif donation_type == 'tobias':
                type_icon = "👤"
            else:
                type_icon = "💝"
            
            print(f"{i:<4} {plan['transaction_id']:<15} {plan['transaction_date'][:10]:<12} "
                  f"€{plan['amount']:>9,.2f} {plan['payee_payer_name']:<30.30} "
                  f"{type_icon} {donation_type:<5} {contact_status}")
    else:
        print(f"{'#':<4} {'Transaction ID':<15} {'Date':<12} {'Amount':<12} {'Payee/Payer':<30} {'Cost Centre':<25} {'Contact'}")
        print("-" * 120)
        
        for i, plan in enumerate(voucher_plan if create_all else [voucher_plan[0]], 1):
            cost_centre_name = plan['cost_centre']['name'] if plan['cost_centre'] else '❌ NOT FOUND'
            contact_status = "✅" if plan['contact'] else "❌"
            print(f"{i:<4} {plan['transaction_id']:<15} {plan['transaction_date'][:10]:<12} "
                  f"€{plan['amount']:>9,.2f} {plan['payee_payer_name']:<30.30} "
                  f"{cost_centre_name:<25.25} {contact_status}")
    
    print()
    print(f"Total: {len(voucher_plan) if create_all else 1} voucher(s) will be created")
    print()


def find_cost_centre_by_name(
    db,
    payee_name: str,
    custom_mappings: Optional[Dict[str, str]] = None
) -> Optional[Dict]:
    """
    Find a cost centre by payee name (case-insensitive).
    
    Args:
        db: Database connection
        payee_name: Name to search for
        custom_mappings: Optional dict of custom name mappings (search_term -> target_name)
                        e.g., {'gwendolyn dewhurst': 'gwen dewhurst'}
        
    Returns:
        Cost centre dict or None
    """
    if not payee_name:
        return None
    
    search_name = payee_name.lower().strip()
    all_cost_centres = db.get_all_cost_centres()
    
    # Check custom mappings first
    if custom_mappings:
        for search_term, target_name in custom_mappings.items():
            if search_term in search_name:
                for cc in all_cost_centres:
                    cc_name = cc.get('name', '').lower()
                    if target_name.lower() in cc_name:
                        return cc
    
    # Default: search for matching cost centre
    for cc in all_cost_centres:
        cc_name = cc.get('name', '').lower().strip()
        if search_name in cc_name or cc_name in search_name:
            return cc
    
    return None


def find_contact_by_name(
    db,
    payee_name: str,
    prefer_category: Optional[int] = None,
    custom_mappings: Optional[Dict[str, str]] = None
) -> Optional[Dict]:
    """
    Find a contact by payee name using advanced fuzzy matching.
    
    Args:
        db: Database connection
        payee_name: Name to search for
        prefer_category: Category ID to prefer (2=Customer, 3=Supplier)
        custom_mappings: Optional dict of custom exact name mappings
                        e.g., {'gwendolyn ruth dewhurst': 'gwen dewhurst'}
        
    Returns:
        Contact dict or None
    """
    if not payee_name:
        return None
    
    import re
    import unicodedata
    
    def normalize_name(name):
        """Normalize name by removing punctuation and extra spaces."""
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
    
    search_name = payee_name.lower().strip()
    search_normalized = normalize_name(search_name)
    all_contacts = db.get_all_contacts()
    
    # Check custom mappings first (exact match)
    if custom_mappings:
        for search_term, target_name in custom_mappings.items():
            if normalize_name(search_term) == search_normalized:
                # Look for exact target name
                for contact in all_contacts:
                    if normalize_name(contact.get('name', '')) == normalize_name(target_name):
                        return contact
    
    search_words_list = search_normalized.split()
    search_words = set(search_words_list)
    
    # Handle "lastname, firstname" format by reversing
    search_alternatives = [search_normalized]
    if ',' in payee_name:
        parts = [p.strip() for p in payee_name.split(',')]
        if len(parts) == 2:
            reversed_name = f"{parts[1]} {parts[0]}"
            search_alternatives.append(normalize_name(reversed_name))
    
    # Search for matching contact by name
    candidate_matches = []
    
    for contact in all_contacts:
        contact_name = contact.get('name', '')
        if not contact_name:
            continue
        
        contact_normalized = normalize_name(contact_name)
        contact_words = set(contact_normalized.split())
        category_id = contact.get('category', {}).get('id') if isinstance(contact.get('category'), dict) else contact.get('category_id')
        
        # Try exact match first with any search alternative
        for i, search_alt in enumerate(search_alternatives):
            if search_alt == contact_normalized:
                priority = 1000 - i
                if prefer_category and category_id == prefer_category:
                    priority += 10000
                candidate_matches.append((priority, contact))
                break
        
        if candidate_matches and candidate_matches[-1][1] == contact:
            continue
        
        # Try partial match
        for i, search_alt in enumerate(search_alternatives):
            if search_alt in contact_normalized or contact_normalized in search_alt:
                priority = 500 - i
                if prefer_category and category_id == prefer_category:
                    priority += 10000
                candidate_matches.append((priority, contact))
                break
        
        if candidate_matches and candidate_matches[-1][1] == contact:
            continue
        
        # Fuzzy word matching
        if search_words and contact_words:
            common_words = search_words & contact_words
            score = len(common_words)
            
            if contact_words.issubset(search_words):
                score += 10
            
            # Check first word matching for multi-word names
            if len(search_words) >= 2 and len(contact_words) >= 2:
                search_parts = search_normalized.split()
                contact_parts = contact_normalized.split()
                
                if common_words and search_parts[0] not in contact_parts and contact_parts[0] not in search_parts:
                    score = 0
            
            if score > 0:
                priority = score
                if prefer_category and category_id == prefer_category:
                    priority += 10000
                candidate_matches.append((priority, contact))
    
    # Return best match
    if candidate_matches:
        candidate_matches.sort(key=lambda x: x[0], reverse=True)
        return candidate_matches[0][1]
    
    return None


def create_voucher_for_transaction(
    client,
    plan: Dict,
    check_account_id: str,
    sev_client_id: str,
    is_income: bool = False
) -> Dict:
    """
    Create a voucher for a transaction.
    
    Args:
        client: SevDesk API client
        plan: Voucher plan dictionary
        check_account_id: The check account ID
        sev_client_id: The sevClient ID
        is_income: Whether this is income (True) or expense (False)
        
    Returns:
        API response dictionary
    """
    amount = abs(float(plan['amount']))
    purpose = plan.get('payment_purpose', '') or ''
    
    # Use custom description if provided (e.g., "202510" for Krankenkassen)
    # Otherwise use voucher_number as fallback
    description = plan.get('description', plan['voucher_number'])
    
    voucher_data = {
        'voucher': {
            'objectName': 'Voucher',
            'mapAll': True,
            'voucherDate': plan['transaction_date'][:10],
            'description': description,
            'payDate': plan['transaction_date'][:10],
            'paymentDeadline': plan['transaction_date'][:10],
            'status': 100,
            'taxType': 'ss',
            'creditDebit': 'D' if is_income else 'C',
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
                'comment': purpose,
            }
        ]
    }
    
    # Add deliveryDate for income vouchers
    if is_income:
        voucher_data['voucher']['deliveryDate'] = plan['transaction_date'][:10]
    
    # Add contact (supplier for expenses, customer for income)
    if plan.get('contact'):
        if is_income:
            # For income, use customer
            voucher_data['voucher']['customer'] = {
                'id': plan['contact']['id'],
                'objectName': 'Contact'
            }
        else:
            # For expenses, use supplier and supplierName
            voucher_data['voucher']['supplier'] = {
                'id': plan['contact']['id'],
                'objectName': 'Contact'
            }
            voucher_data['voucher']['supplierName'] = plan['payee_payer_name']
    else:
        # No contact found - set supplierName as fallback for expenses
        if not is_income:
            voucher_data['voucher']['supplierName'] = plan['payee_payer_name']
    
    # Add cost centre (on both voucher and position level)
    if plan.get('cost_centre'):
        voucher_data['voucher']['costCentre'] = {
            'id': plan['cost_centre']['id'],
            'objectName': 'CostCentre'
        }
        voucher_data['voucherPosSave'][0]['costCentre'] = {
            'id': plan['cost_centre']['id'],
            'objectName': 'CostCentre'
        }
    
    # Create the voucher
    response = client.create_voucher(voucher_data)
    return response
