#!/usr/bin/env python3
"""
Create vouchers for KONTAKTMISSION DEUTSCHLAND donation expenses.

This script finds open transactions to KONTAKTMISSION DEUTSCHLAND
and creates vouchers for them.

Cost centre is determined based on payment purpose:
- Contains "Hodzi" → Cost Centre: "Hodzi"
- Contains "Jean" or "Richards" → Cost Centre: "Samuel Jeanrichard (intern)"
- Otherwise → No cost centre

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


# Cost centre mappings based on purpose
COST_CENTRE_MAPPINGS = {
    'hodzi': 'Hodzi',
    'jean richards': 'Samuel Jeanrichard (intern)',
    'jeanrichard': 'Samuel Jeanrichard (intern)',
}

# Contact name for KONTAKTMISSION
KONTAKTMISSION_CONTACT = 'KONTAKTMISSION DEUTSCHLAND'


class KontaktmissionVoucherCreator(VoucherCreatorBase):
    """Voucher creator for KONTAKTMISSION DEUTSCHLAND donations."""
    
    def get_script_name(self) -> str:
        """Return script name."""
        return "KONTAKTMISSION"
    
    def get_accounting_type_name(self) -> str:
        """Return accounting type name to search for."""
        return "Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke"
    
    def get_markdown_output_file(self) -> str:
        """Get the output markdown filename."""
        return "voucher_plan_kontaktmission.md"
    
    def get_script_filename(self) -> str:
        """Get the script filename for help text."""
        return "create_vouchers_for_kontaktmission.py"
    
    def filter_transactions(self, all_transactions: List[Dict]) -> List[Dict]:
        """Filter transactions for KONTAKTMISSION."""
        kontakt_transactions = []
        for txn in all_transactions:
            raw_data = json.loads(txn.get('raw_data', '{}'))
            payee = raw_data.get('payeePayerName', '') or ''
            purpose = txn.get('paymt_purpose', '') or ''
            
            # Only include expense transactions (negative amounts)
            if txn.get('amount', 0) < 0:
                if 'KONTAKTMISSION' in payee.upper() or 'KONTAKTMISSION' in purpose.upper():
                    kontakt_transactions.append(txn)
        
        return kontakt_transactions
    
    def build_voucher_plan_item(
        self,
        transaction: Dict,
        voucher_number: str,
        index: int
    ) -> Dict:
        """Build voucher plan item for a KONTAKTMISSION transaction."""
        # Parse raw data to get payeePayerName
        raw_data = json.loads(transaction.get('raw_data', '{}'))
        payee_payer_name = raw_data.get('payeePayerName', 'Unknown')
        payment_purpose = transaction.get('paymt_purpose', '') or ''
        
        # Determine cost centre based on payment purpose
        cost_centre = self._determine_cost_centre(payment_purpose)
        
        # Find matching contact (use KONTAKTMISSION as payee)
        contact = find_contact_by_name(
            self.db,
            KONTAKTMISSION_CONTACT,
            prefer_category=3
        )
        
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
    
    def _determine_cost_centre(self, payment_purpose: str) -> dict:
        """
        Determine cost centre based on payment purpose.
        
        Args:
            payment_purpose: Payment purpose text
            
        Returns:
            Cost centre dict or None
        """
        purpose_upper = payment_purpose.upper()
        
        # Check for Hodzi
        if 'HODZI' in purpose_upper:
            return find_cost_centre_by_name(
                self.db,
                'Hodzi',
                custom_mappings=COST_CENTRE_MAPPINGS
            )
        
        # Check for Jean Richards
        if 'JEAN' in purpose_upper or 'RICHARDS' in purpose_upper:
            return find_cost_centre_by_name(
                self.db,
                'Jean Richards',
                custom_mappings=COST_CENTRE_MAPPINGS
            )
        
        return None
    
    def is_income_voucher(self) -> bool:
        """KONTAKTMISSION donations are expenses."""
        return False


def main():
    """Main function."""
    creator = KontaktmissionVoucherCreator()
    creator.run()


if __name__ == '__main__':
    main()
