#!/usr/bin/env python3
"""
Create vouchers for Gehalt (Salary) transactions.

This script finds open transactions containing "Gehalt" in the payment purpose
and creates vouchers for them.

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


# Custom mappings for Gehalt script
COST_CENTRE_MAPPINGS = {
    'gwendolyn dewhurst': 'gwen dewhurst',
    'samuel jeanrichard': 'samuel jeanrichard (intern)',
}

CONTACT_MAPPINGS = {
    'gwendolyn ruth dewhurst': 'gwen dewhurst',
}


class GehaltVoucherCreator(VoucherCreatorBase):
    """Voucher creator for Gehalt (Salary) transactions."""
    
    def get_script_name(self) -> str:
        """Return script name."""
        return "Gehalt"
    
    def get_accounting_type_name(self) -> str:
        """Return accounting type name to search for."""
        return "Lohn / Gehalt"
    
    def filter_transactions(self, all_transactions: List[Dict]) -> List[Dict]:
        """Filter transactions containing 'Gehalt' in payment purpose."""
        gehalt_transactions = []
        for txn in all_transactions:
            payment_purpose = txn.get('paymt_purpose', '') or ''
            payment_purpose_lower = payment_purpose.lower()
            if 'gehalt' in payment_purpose_lower:
                gehalt_transactions.append(txn)
        return gehalt_transactions
    
    def build_voucher_plan_item(
        self,
        transaction: Dict,
        voucher_number: str,
        index: int
    ) -> Dict:
        """Build voucher plan item for a Gehalt transaction."""
        # Parse raw data to get payeePayerName
        raw_data = json.loads(transaction.get('raw_data', '{}'))
        payee_payer_name = raw_data.get('payeePayerName', 'Unknown')
        
        # Find matching cost centre and contact
        cost_centre = self._find_gehalt_cost_centre(payee_payer_name)
        contact = self._find_gehalt_contact(payee_payer_name)
        
        return {
            'transaction_id': transaction['id'],
            'transaction_date': transaction['value_date'],
            'amount': transaction['amount'],
            'payment_purpose': transaction['paymt_purpose'],
            'payee_payer_name': payee_payer_name,
            'cost_centre': cost_centre,
            'contact': contact,
            'voucher_number': voucher_number,
            'accounting_type': self.accounting_type
        }
    
    def _find_gehalt_cost_centre(self, payee_name: str) -> dict:
        """Find cost centre for Gehalt with custom mappings."""
        return find_cost_centre_by_name(
            self.db,
            payee_name,
            custom_mappings=COST_CENTRE_MAPPINGS
        )
    
    def _find_gehalt_contact(self, payee_name: str) -> dict:
        """Find contact for Gehalt (prefer Suppliers for expenses)."""
        return find_contact_by_name(
            self.db,
            payee_name,
            prefer_category=3,
            custom_mappings=CONTACT_MAPPINGS
        )
    
    def is_income_voucher(self) -> bool:
        """Gehalt is an expense."""
        return False


def main():
    """Main function."""
    creator = GehaltVoucherCreator()
    creator.run()


if __name__ == '__main__':
    main()
