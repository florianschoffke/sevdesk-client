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

REFACTORED VERSION using VoucherCreatorBase.
"""
import os
import sys
import json
from typing import List, Dict, Optional

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.vouchers.voucher_creator_base import VoucherCreatorBase
from src.vouchers.voucher_utils import find_contact_by_name


# Cost centre names for different donation types
COST_CENTRE_NAMES = {
    'mission': 'Spendeneingänge Missionare',
    'general': 'Spendeneingänge Konto',
    'jeske': 'Jeske (Durchlaufende Posten)',
    'tobias': 'Tobias Zimmermann (Spende für Tobias)',
}


class SpendenVoucherCreator(VoucherCreatorBase):
    """Voucher creator for Spenden (Donations) transactions."""
    
    def __init__(self):
        """Initialize the creator."""
        super().__init__()
        self.cost_centres = {}  # Dict of donation_type -> cost_centre
    
    def get_script_name(self) -> str:
        """Return script name."""
        return "Spenden"
    
    def get_accounting_type_name(self) -> str:
        """Return accounting type name to search for."""
        return "Spendeneingang"
    
    def find_accounting_type(self, db) -> bool:
        """
        Find accounting type and also load all cost centres for donation types.
        
        Returns:
            True if found, False otherwise
        """
        # First find the accounting type using parent implementation
        if not super().find_accounting_type(db):
            return False
        
        # Also find cost centres for all donation types
        missing_cost_centres = []
        
        for donation_type, cc_name in COST_CENTRE_NAMES.items():
            cc = self._find_cost_centre_by_exact_name(db, cc_name)
            if cc:
                self.cost_centres[donation_type] = cc
                print(f"✓ Found cost centre ({donation_type}): {cc['name']} (ID: {cc['id']})")
            else:
                missing_cost_centres.append(cc_name)
                print(f"❌ Missing cost centre ({donation_type}): {cc_name}")
        
        print()
        
        if missing_cost_centres:
            print("Error: Required cost centres not found:")
            for cc_name in missing_cost_centres:
                print(f"  - {cc_name}")
            return False
        
        return True
    
    def filter_transactions(self, all_transactions: List[Dict]) -> List[Dict]:
        """Filter transactions with donation keywords and positive amounts."""
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
        
        # Determine donation type and cost centre
        payment_purpose = transaction.get('paymt_purpose')
        donation_type, cost_centre = self._determine_donation_type_and_cost_centre(payment_purpose)
        
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
        payment_purpose: str
    ) -> tuple:
        """
        Determine donation type and select appropriate cost centre.
        
        Returns:
            Tuple of (donation_type, cost_centre)
        """
        if not payment_purpose:
            return ('general', self.cost_centres['general'])
        
        purpose = payment_purpose
        purpose_lower = payment_purpose.lower()
        
        # Special rules for specific donation purposes (checked first)
        if 'Artur Jeske' in purpose:
            return ('jeske', self.cost_centres['jeske'])
        
        # Check for Tobias Zimmermann donations (multiple patterns)
        if 'Spende Tobias Zimmermann' in purpose or 'Tobi Zimmermann' in purpose:
            return ('tobias', self.cost_centres['tobias'])
        
        # Check for mission-related keywords
        if 'mission' in purpose_lower or 'missionar' in purpose_lower:
            return ('mission', self.cost_centres['mission'])
        
        # Default: general donation
        return ('general', self.cost_centres['general'])
    
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
