#!/usr/bin/env python3
"""
Create vouchers for JEK Freizeit (JEK Leisure) income transactions.

This script finds open incoming transactions with "JEK Freizeit" or "JEK Leisure"
in the payment purpose and creates vouchers for them.

Uses:
- Accounting Type: "Durchlaufende Posten"
- Cost Centre: "JEK Freizeiten"

REFACTORED VERSION using VoucherCreatorBase.
"""
import os
import sys
import json
from typing import List, Dict

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.vouchers.voucher_creator_base import VoucherCreatorBase
from src.vouchers.voucher_utils import find_cost_centre_by_name, find_contact_by_name


# Cost centre for JEK Freizeiten
COST_CENTRE_NAME = 'JEK Freizeiten'


class JEKFreizeitVoucherCreator(VoucherCreatorBase):
    """Voucher creator for JEK Freizeit (JEK Leisure) income transactions."""
    
    def __init__(self):
        """Initialize the creator."""
        super().__init__()
        self.cost_centre = None  # Will be loaded in find_accounting_type
    
    def get_script_name(self) -> str:
        """Return script name."""
        return "JEK Freizeit"
    
    def get_accounting_type_name(self) -> str:
        """Return accounting type name to search for."""
        return "Durchlaufende Posten"
    
    def get_markdown_output_file(self) -> str:
        """Get the output markdown filename."""
        return "voucher_plan_jek_freizeit.md"
    
    def get_script_filename(self) -> str:
        """Get the script filename for help text."""
        return "create_vouchers_for_jek_freizeit.py"
    
    def find_accounting_type(self, db) -> bool:
        """
        Find accounting type and also load the JEK Freizeiten cost centre.
        
        Returns:
            True if both found, False otherwise
        """
        # First find the accounting type using parent implementation
        if not super().find_accounting_type(db):
            return False
        
        # Find the JEK Freizeiten cost centre (use exact match to avoid matching just "JEK")
        all_cost_centres = db.get_all_cost_centres()
        self.cost_centre = None
        for cc in all_cost_centres:
            if cc.get('name', '').strip() == COST_CENTRE_NAME:
                self.cost_centre = cc
                break
        
        if not self.cost_centre:
            print(f"Error: Could not find cost centre '{COST_CENTRE_NAME}'!")
            print("\nAvailable JEK-related cost centres:")
            for cc in all_cost_centres:
                if 'JEK' in cc.get('name', '').upper():
                    print(f"  - {cc.get('name')} (ID: {cc.get('id')})")
            return False
        
        print(f"✓ Found cost centre: {self.cost_centre['name']} (ID: {self.cost_centre['id']})")
        print()
        return True
    
    def filter_transactions(self, all_transactions: List[Dict]) -> List[Dict]:
        """Filter transactions for JEK Freizeit/Leisure income."""
        jek_transactions = []
        for txn in all_transactions:
            purpose = txn.get('paymt_purpose', '') or ''
            amount = float(txn.get('amount', 0))
            
            # Only include income transactions (positive amounts)
            if amount > 0:
                purpose_upper = purpose.upper()
                
                # Check for JEK Freizeit or JEK Leisure
                if ('JEK FREIZEIT' in purpose_upper or 
                    'JEK LEISURE' in purpose_upper):
                    jek_transactions.append(txn)
        
        return jek_transactions
    
    def build_voucher_plan_item(
        self,
        transaction: Dict,
        voucher_number: str,
        index: int
    ) -> Dict:
        """Build voucher plan item for a JEK Freizeit transaction."""
        # Parse raw data to get payeePayerName
        raw_data = json.loads(transaction.get('raw_data', '{}'))
        payee_payer_name = raw_data.get('payeePayerName', 'Unknown')
        
        # Try to find matching contact (payer)
        contact = find_contact_by_name(
            self.db,
            payee_payer_name,
            prefer_category=1  # Prefer Kunden (customers)
        )
        
        return {
            'transaction_id': transaction['id'],
            'transaction_date': transaction['value_date'],
            'amount': transaction['amount'],
            'payment_purpose': transaction['paymt_purpose'],
            'payee_payer_name': payee_payer_name,
            'cost_centre': self.cost_centre,  # Same for all (JEK Freizeiten)
            'contact': contact,
            'voucher_number': voucher_number,
            'accounting_type': self.accounting_type
        }
    
    def is_income_voucher(self) -> bool:
        """JEK Freizeit are income transactions."""
        return True


def main():
    """Main function."""
    creator = JEKFreizeitVoucherCreator()
    creator.run()


if __name__ == '__main__':
    main()
