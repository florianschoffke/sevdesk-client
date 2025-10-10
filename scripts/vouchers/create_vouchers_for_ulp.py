#!/usr/bin/env python3
"""
Create vouchers for ÜLP (Übungsleiterpauschale) transactions.

This script finds open transactions containing "ÜLP" or "Übungsleiterpauschale"
in the payment purpose and creates vouchers for them.

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


# Custom mappings for ÜLP script
COST_CENTRE_MAPPINGS = {
    'tobias zimmermann': 'tobias zimmermann (ülp)',  # Special rule for ÜLP
}

CONTACT_MAPPINGS = {
    # Add any custom contact mappings here if needed
}


class UlpVoucherCreator(VoucherCreatorBase):
    """Voucher creator for ÜLP (Übungsleiterpauschale) transactions."""
    
    def get_script_name(self) -> str:
        """Return script name."""
        return "ÜLP"
    
    def get_accounting_type_name(self) -> str:
        """Return accounting type name to search for."""
        # Will match both "Ehrenamtspauschale" and "Übungsleiterpauschale"
        return "pauschale"
    
    def filter_transactions(self, all_transactions: List[Dict]) -> List[Dict]:
        """Filter transactions containing ÜLP, Übungsleiterpauschale or Ehrenamtspauschale."""
        ulp_transactions = []
        for txn in all_transactions:
            payment_purpose = txn.get('paymt_purpose', '') or ''
            payment_purpose_lower = payment_purpose.lower()
            if ('ülp' in payment_purpose_lower or 
                'übungsleiterpauschale' in payment_purpose_lower or
                'ehrenamtspauschale' in payment_purpose_lower):
                ulp_transactions.append(txn)
        return ulp_transactions
    
    def build_voucher_plan_item(
        self,
        transaction: Dict,
        voucher_number: str,
        index: int
    ) -> Dict:
        """Build voucher plan item for a ÜLP transaction."""
        # Parse raw data to get payeePayerName
        raw_data = json.loads(transaction.get('raw_data', '{}'))
        payee_payer_name = raw_data.get('payeePayerName', 'Unknown')
        
        # Check if this is a ÜLP transaction (for special cost centre rule)
        payment_purpose = transaction.get('paymt_purpose', '') or ''
        is_ulp = 'ÜLP' in payment_purpose
        
        # Find matching cost centre (with special rule for Tobias + ÜLP)
        cost_centre = self._find_ulp_cost_centre(payee_payer_name, is_ulp)
        
        # Find matching contact (supplier)
        contact = self._find_ulp_contact(payee_payer_name)
        
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
    
    def _find_ulp_cost_centre(self, payee_name: str, is_ulp_transaction: bool) -> dict:
        """
        Find cost centre for ÜLP transactions with special rules.
        
        Args:
            payee_name: Name to search for
            is_ulp_transaction: Whether this is a ÜLP transaction
        """
        # Special rule: For Tobias Zimmermann + ÜLP transaction, use "Tobias Zimmermann (ÜLP)"
        mappings = COST_CENTRE_MAPPINGS if is_ulp_transaction else {}
        return find_cost_centre_by_name(
            self.db,
            payee_name,
            custom_mappings=mappings
        )
    
    def _find_ulp_contact(self, payee_name: str) -> dict:
        """Find contact for ÜLP transactions (prefer Suppliers for expenses)."""
        return find_contact_by_name(
            self.db,
            payee_name,
            prefer_category=3,
            custom_mappings=CONTACT_MAPPINGS
        )
    
    def is_income_voucher(self) -> bool:
        """ÜLP is an expense."""
        return False


def main():
    """Main function."""
    creator = UlpVoucherCreator()
    creator.run()


if __name__ == '__main__':
    main()
