#!/usr/bin/env python3
"""
Create vouchers for EBTC donation expenses.

This script finds open outgoing transactions to EBTC where the payment purpose
contains "Spende" and creates vouchers for them.

Uses:
- Accounting Type: "Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke"
- Cost Centre: "Spendenausgänge"

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


# Cost centre for outgoing donations
COST_CENTRE_NAME = 'Spendenausgänge'

# EBTC contact name (we'll search for variations)
EBTC_CONTACT_NAMES = ['EBTC', 'Europäisches Bibel Trainings Centrum']


class EBTCVoucherCreator(VoucherCreatorBase):
    """Voucher creator for EBTC donations."""
    
    def __init__(self):
        """Initialize the creator."""
        super().__init__()
        self.cost_centre = None  # Will be loaded in find_accounting_type
    
    def get_script_name(self) -> str:
        """Return script name."""
        return "EBTC"
    
    def get_accounting_type_name(self) -> str:
        """Return accounting type name to search for."""
        return "Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke"
    
    def get_markdown_output_file(self) -> str:
        """Get the output markdown filename."""
        return "voucher_plan_ebtc.md"
    
    def get_script_filename(self) -> str:
        """Get the script filename for help text."""
        return "create_vouchers_for_ebtc.py"
    
    def find_accounting_type(self, db) -> bool:
        """
        Find accounting type and also load the Spendenausgänge cost centre.
        
        Returns:
            True if both found, False otherwise
        """
        # First find the accounting type using parent implementation
        if not super().find_accounting_type(db):
            return False
        
        # Also find the Spendenausgänge cost centre
        self.cost_centre = find_cost_centre_by_name(db, COST_CENTRE_NAME)
        if not self.cost_centre:
            print(f"Error: Could not find cost centre '{COST_CENTRE_NAME}'!")
            return False
        
        print(f"✓ Found cost centre: {self.cost_centre['name']} (ID: {self.cost_centre['id']})")
        print()
        return True
    
    def filter_transactions(self, all_transactions: List[Dict]) -> List[Dict]:
        """Filter transactions for EBTC donations (outgoing with 'Spende' in purpose)."""
        ebtc_transactions = []
        for txn in all_transactions:
            raw_data = json.loads(txn.get('raw_data', '{}'))
            payee = raw_data.get('payeePayerName', '') or ''
            purpose = txn.get('paymt_purpose', '') or ''
            amount = float(txn.get('amount', 0))
            
            # Only include expense transactions (negative amounts)
            if amount < 0:
                # Check if EBTC is the recipient
                payee_upper = payee.upper()
                purpose_upper = purpose.upper()
                
                is_ebtc = 'EBTC' in payee_upper or 'EBTC' in purpose_upper
                has_spende = 'SPENDE' in purpose_upper or 'Spende' in purpose
                
                if is_ebtc and has_spende:
                    ebtc_transactions.append(txn)
        
        return ebtc_transactions
    
    def build_voucher_plan_item(
        self,
        transaction: Dict,
        voucher_number: str,
        index: int
    ) -> Dict:
        """Build voucher plan item for an EBTC transaction."""
        # Parse raw data to get payeePayerName
        raw_data = json.loads(transaction.get('raw_data', '{}'))
        payee_payer_name = raw_data.get('payeePayerName', 'Unknown')
        
        # Find matching contact (try to find EBTC)
        contact = None
        for contact_name in EBTC_CONTACT_NAMES:
            contact = find_contact_by_name(
                self.db,
                contact_name,
                prefer_category=3  # Prefer Lieferanten (suppliers)
            )
            if contact:
                break
        
        if not contact:
            # If not found, try with the actual payee name
            contact = find_contact_by_name(
                self.db,
                payee_payer_name,
                prefer_category=3
            )
        
        return {
            'transaction_id': transaction['id'],
            'transaction_date': transaction['value_date'],
            'amount': transaction['amount'],
            'payment_purpose': transaction['paymt_purpose'],
            'payee_payer_name': payee_payer_name,
            'cost_centre': self.cost_centre,  # Same for all (Spendenausgänge)
            'contact': contact,
            'voucher_number': voucher_number,
            'accounting_type': self.accounting_type
        }
    
    def is_income_voucher(self) -> bool:
        """EBTC donations are expenses."""
        return False


def main():
    """Main function."""
    creator = EBTCVoucherCreator()
    creator.run()


if __name__ == '__main__':
    main()
