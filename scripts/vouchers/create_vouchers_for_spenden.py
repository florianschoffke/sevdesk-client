#!/usr/bin/env python3
"""
Create vouchers for Spenden (Donations) transactions.

This script finds open incoming transactions (amount > 0) with donation-related keywords
in the payment purpose and creates vouchers for them.

Donation matching rules are configured in config/donation_rules.csv with support for:
- Filter rules: Determine if a transaction is a donation based on payer name or purpose patterns
- Type rules: Determine donation type and cost centre based on patterns (with priority)
- Match modes: 'contains', 'startswith', or 'exact' matching

All use Accounting Type: "Spendeneingang"

REFACTORED VERSION using VoucherCreatorBase and external CSV configuration.
"""
import os
import sys
import json
import csv
from typing import List, Dict, Optional, Tuple

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.vouchers.voucher_creator_base import VoucherCreatorBase
from src.vouchers.voucher_utils import find_contact_by_name


class DonationRule:
    """Represents a donation matching rule from CSV."""
    
    def __init__(self, rule_dict: Dict):
        """Initialize rule from CSV row."""
        self.rule_type = rule_dict.get('rule_type', '')
        self.payer_name_pattern = rule_dict.get('payer_name_pattern', '').strip()
        self.purpose_pattern = rule_dict.get('purpose_pattern', '').strip()
        self.donation_type = rule_dict.get('donation_type', '').strip()
        self.cost_centre_name = rule_dict.get('cost_centre_name', '').strip()
        self.priority = int(rule_dict.get('priority', 999))
        self.match_mode = rule_dict.get('match_mode', 'contains').strip()
    
    def matches(self, payer_name: str, purpose: str) -> bool:
        """Check if this rule matches the given payer name and purpose."""
        # Check payer name pattern if specified
        if self.payer_name_pattern:
            if not self._pattern_matches(payer_name or '', self.payer_name_pattern):
                return False
        
        # Check purpose pattern if specified
        if self.purpose_pattern:
            if not self._pattern_matches(purpose or '', self.purpose_pattern):
                return False
        
        # If we get here, all specified patterns matched (or no patterns were specified)
        return True
    
    def _pattern_matches(self, text: str, pattern: str) -> bool:
        """Check if pattern matches text based on match mode."""
        if self.match_mode == 'exact':
            return text == pattern
        elif self.match_mode == 'startswith':
            return text.startswith(pattern)
        else:  # contains (default)
            return pattern in text


class SpendenVoucherCreator(VoucherCreatorBase):
    """Voucher creator for Spenden (Donations) transactions."""
    
    def __init__(self):
        """Initialize the creator."""
        super().__init__()
        self.cost_centres = {}  # Dict of donation_type -> cost_centre
        self.filter_rules: List[DonationRule] = []
        self.type_rules: List[DonationRule] = []
        self.cost_centre_names = set()  # Track unique cost centre names
        self._load_donation_rules()
    
    def _load_donation_rules(self):
        """Load donation rules from CSV file."""
        config_path = os.path.join(project_root, 'config', 'donation_rules.csv')
        
        if not os.path.exists(config_path):
            print(f"❌ Error: Donation rules file not found: {config_path}")
            print("   Please create config/donation_rules.csv with donation matching rules.")
            sys.exit(1)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip comment lines and empty lines
                if not row.get('rule_type') or row.get('rule_type').startswith('#'):
                    continue
                
                rule = DonationRule(row)
                
                if rule.rule_type == 'filter':
                    self.filter_rules.append(rule)
                elif rule.rule_type == 'type':
                    self.type_rules.append(rule)
                    if rule.cost_centre_name:
                        self.cost_centre_names.add(rule.cost_centre_name)
        
        # Sort type rules by priority (lower number = higher priority)
        self.type_rules.sort(key=lambda r: r.priority)
        
        print(f"✓ Loaded {len(self.filter_rules)} filter rules and {len(self.type_rules)} type rules from CSV")
        print(f"✓ Found {len(self.cost_centre_names)} unique cost centres in rules")
        print()

    
    def get_script_name(self) -> str:
        """Return script name."""
        return "Spenden"
    
    def get_accounting_type_name(self) -> str:
        """Return accounting type name to search for."""
        return "Spendeneingang"
    
    def find_accounting_type(self, db) -> bool:
        """
        Find accounting type and also load all cost centres from rules.
        
        Returns:
            True if found, False otherwise
        """
        # First find the accounting type using parent implementation
        if not super().find_accounting_type(db):
            return False
        
        # Load cost centres based on unique names from rules
        missing_cost_centres = []
        
        for cc_name in sorted(self.cost_centre_names):
            cc = self._find_cost_centre_by_exact_name(db, cc_name)
            if cc:
                self.cost_centres[cc_name] = cc
                print(f"✓ Found cost centre: {cc['name']} (ID: {cc['id']})")
            else:
                missing_cost_centres.append(cc_name)
                print(f"❌ Missing cost centre: {cc_name}")
        
        print()
        
        if missing_cost_centres:
            print("Error: Required cost centres not found:")
            for cc_name in missing_cost_centres:
                print(f"  - {cc_name}")
            return False
        
        return True
    
    def filter_transactions(self, all_transactions: List[Dict]) -> List[Dict]:
        """Filter transactions with donation keywords and positive amounts using CSV rules."""
        spenden_transactions = []
        for txn in all_transactions:
            payment_purpose = txn.get('paymt_purpose', '') or ''
            amount = float(txn.get('amount', 0))
            
            # Must be income (positive)
            if amount > 0:
                # Get payer name from raw data
                raw_data = json.loads(txn.get('raw_data', '{}'))
                payee_payer_name = raw_data.get('payeePayerName', '')
                
                # Check if any filter rule matches
                is_spende = any(
                    rule.matches(payee_payer_name, payment_purpose)
                    for rule in self.filter_rules
                )
                
                if is_spende:
                    spenden_transactions.append(txn)
        
        return spenden_transactions
    
    def build_voucher_plan_item(
        self,
        transaction: Dict,
        voucher_number: str,
        index: int
    ) -> Dict:
        """Build voucher plan item for a Spenden transaction."""
        # Parse raw data to get payeePayerName
        raw_data = json.loads(transaction.get('raw_data', '{}'))
        payee_payer_name = raw_data.get('payeePayerName', 'Unknown')
        
        # Determine donation type and cost centre using CSV rules
        payment_purpose = transaction.get('paymt_purpose')
        donation_type, cost_centre = self._determine_donation_type_and_cost_centre(
            payment_purpose,
            payee_payer_name
        )
        
        # Find matching contact (donor) - IMPORTANT for tax tracking!
        contact = self._find_spenden_contact(payee_payer_name)
        
        return {
            'transaction_id': transaction['id'],
            'transaction_date': transaction['value_date'],
            'amount': transaction['amount'],
            'payment_purpose': transaction['paymt_purpose'],
            'payee_payer_name': payee_payer_name,
            'donation_type': donation_type,
            'cost_centre': cost_centre,
            'contact': contact,
            'voucher_number': voucher_number,
            'accounting_type': self.accounting_type
        }
    
    def show_donation_type_column(self) -> bool:
        """Show donation type column for Spenden."""
        return True
    
    def get_extra_markdown_sections(self, voucher_plan: List[Dict]) -> Optional[List[str]]:
        """Add donation type statistics to markdown."""
        # Count donation types
        type_counts = {
            'mission': sum(1 for p in voucher_plan if p.get('donation_type') == 'mission'),
            'general': sum(1 for p in voucher_plan if p.get('donation_type') == 'general'),
            'jeske': sum(1 for p in voucher_plan if p.get('donation_type') == 'jeske'),
            'tobias': sum(1 for p in voucher_plan if p.get('donation_type') == 'tobias'),
        }
        
        extra_sections = []
        extra_sections.append("## Donation Type Statistics")
        extra_sections.append("")
        extra_sections.append(f"- 🎯 Mission donations: {type_counts['mission']}")
        extra_sections.append(f"- 💝 General donations: {type_counts['general']}")
        extra_sections.append(f"- 🔄 Jeske donations: {type_counts['jeske']}")
        extra_sections.append(f"- 👤 Tobias donations: {type_counts['tobias']}")
        extra_sections.append(f"- **Total**: {len(voucher_plan)} donations")
        extra_sections.append("")
        
        return extra_sections
    
    def print_plan_summary(self, voucher_plan: List[Dict], output_file: str):
        """Print summary with donation type breakdown."""
        # Count donation types
        type_counts = {
            'mission': sum(1 for p in voucher_plan if p.get('donation_type') == 'mission'),
            'general': sum(1 for p in voucher_plan if p.get('donation_type') == 'general'),
            'jeske': sum(1 for p in voucher_plan if p.get('donation_type') == 'jeske'),
            'tobias': sum(1 for p in voucher_plan if p.get('donation_type') == 'tobias'),
        }
        
        missing_contacts = [p for p in voucher_plan if not p.get('contact')]
        
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
        print(f"  → {self.accounting_type['name']} (ID: {self.accounting_type['id']})")
        print()
        print("Next steps:")
        print(f"  1. Open and review: {output_file}")
        print(f"  2. Test with single voucher: python {self.get_script_filename()} --create-single")
        print(f"  3. Create all vouchers: python {self.get_script_filename()} --create-all")
        print()
        print("=" * 80)
    
    def is_income_voucher(self) -> bool:
        """Spenden is income."""
        return True
    
    # Helper methods
    
    def _find_cost_centre_by_exact_name(self, db, name: str) -> Optional[Dict]:
        """Find a cost centre by exact name match."""
        if not name:
            return None
        
        all_cost_centres = db.get_all_cost_centres()
        for cc in all_cost_centres:
            if cc.get('name') == name:
                return cc
        return None
    
    def _determine_donation_type_and_cost_centre(
        self,
        payment_purpose: str,
        payer_name: str = ''
    ) -> Tuple[str, Dict]:
        """
        Determine donation type and select appropriate cost centre using CSV rules.
        Rules are checked in priority order (lower priority number = checked first).
        
        Args:
            payment_purpose: Payment purpose text
            payer_name: Payer name (optional)
        
        Returns:
            Tuple of (donation_type, cost_centre)
        """
        # Check type rules in priority order
        for rule in self.type_rules:
            if rule.matches(payer_name, payment_purpose or ''):
                # Found matching rule
                cost_centre = self.cost_centres.get(rule.cost_centre_name)
                if cost_centre:
                    return (rule.donation_type, cost_centre)
                else:
                    print(f"⚠️  Warning: Rule matched but cost centre not found: {rule.cost_centre_name}")
        
        # Fallback: should not happen if rules are properly configured with a catch-all rule
        print(f"⚠️  Warning: No matching type rule for payer='{payer_name}' purpose='{payment_purpose}'")
        # Try to return first available cost centre
        if self.cost_centres:
            first_cc = next(iter(self.cost_centres.values()))
            return ('general', first_cc)
        
        raise ValueError("No cost centres available and no matching rule found")
    
    def _find_spenden_contact(self, payee_name: str) -> Optional[Dict]:
        """
        Find contact for Spenden (prefer Customers for income).
        Uses enhanced matching with first-name prioritization for multi-name payees.
        """
        return find_contact_by_name(self.db, payee_name, prefer_category=2)


def main():
    """Main function."""
    creator = SpendenVoucherCreator()
    creator.run()


if __name__ == '__main__':
    main()
