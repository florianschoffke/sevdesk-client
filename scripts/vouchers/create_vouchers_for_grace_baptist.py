#!/usr/bin/env python3
"""
Create vouchers for GRACE BAPTIST TAMPERE RY donation expenses.

This script finds open transactions to GRACE BAPTIST TAMPERE RY
for Miska Wilhelmsson and creates vouchers for them.

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


# Cost centre for Wilhelmsson
COST_CENTRE_NAME = 'Wilhelmson'

# Contact name for GRACE BAPTIST
GRACE_BAPTIST_CONTACT = 'GRACE BAPTIST TAMPERE RY'


class GraceBaptistVoucherCreator(VoucherCreatorBase):
    """Voucher creator for GRACE BAPTIST TAMPERE RY donations."""
    
    def __init__(self):
        """Initialize the creator."""
        super().__init__()
        self.cost_centre = None  # Will be loaded in find_accounting_type
    
    def get_script_name(self) -> str:
        """Return script name."""
        return "GRACE BAPTIST"
    
    def get_accounting_type_name(self) -> str:
        """Return accounting type name to search for."""
        return "Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke"
    
    def get_markdown_output_file(self) -> str:
        """Get the output markdown filename."""
        return "voucher_plan_grace_baptist.md"
    
    def get_script_filename(self) -> str:
        """Get the script filename for help text."""
        return "create_vouchers_for_grace_baptist.py"
    
    def find_accounting_type(self, db) -> bool:
        """
        Find accounting type and also load the Wilhelmsson cost centre.
        
        Returns:
            True if both found, False otherwise
        """
        # First find the accounting type using parent implementation
        if not super().find_accounting_type(db):
            return False
        
        # Also find the Wilhelmsson cost centre
        self.cost_centre = find_cost_centre_by_name(db, COST_CENTRE_NAME)
        if not self.cost_centre:
            print(f"Error: Could not find cost centre '{COST_CENTRE_NAME}'!")
            return False
        
        print(f"✓ Found cost centre: {self.cost_centre['name']} (ID: {self.cost_centre['id']})")
        print()
        return True
    
    def filter_transactions(self, all_transactions: List[Dict]) -> List[Dict]:
        """Filter transactions for GRACE BAPTIST with WILHELMSSON."""
        grace_transactions = []
        for txn in all_transactions:
            raw_data = json.loads(txn.get('raw_data', '{}'))
            payee = raw_data.get('payeePayerName', '') or ''
            purpose = txn.get('paymt_purpose', '') or ''
            
            # Only include expense transactions (negative amounts)
            if txn.get('amount', 0) < 0:
                if ('GRACE BAPTIST' in payee.upper() or 'GRACE BAPTIST' in purpose.upper()):
                    if 'MISKA WILHELMSSON' in purpose.upper() or 'WILHELMSSON' in purpose.upper():
                        grace_transactions.append(txn)
        
        return grace_transactions
    
    def build_voucher_plan_item(
        self,
        transaction: Dict,
        voucher_number: str,
        index: int
    ) -> Dict:
        """Build voucher plan item for a GRACE BAPTIST transaction."""
        # Parse raw data to get payeePayerName
        raw_data = json.loads(transaction.get('raw_data', '{}'))
        payee_payer_name = raw_data.get('payeePayerName', 'Unknown')
        
        # Find matching contact (use GRACE BAPTIST as payee)
        contact = find_contact_by_name(
            self.db,
            GRACE_BAPTIST_CONTACT,
            prefer_category=3
        )
        
        return {
            'transaction_id': transaction['id'],
            'transaction_date': transaction['value_date'],
            'amount': transaction['amount'],
            'payment_purpose': transaction['paymt_purpose'],
            'payee_payer_name': payee_payer_name,
            'cost_centre': self.cost_centre,  # Same for all
            'contact': contact,
            'voucher_number': voucher_number,
            'accounting_type': self.accounting_type
        }
    
    def is_income_voucher(self) -> bool:
        """GRACE BAPTIST donations are expenses."""
        return False


def main():
    """Main function."""
    creator = GraceBaptistVoucherCreator()
    creator.run()


if __name__ == '__main__':
    main()
