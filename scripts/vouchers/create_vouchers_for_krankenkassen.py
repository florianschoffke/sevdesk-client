#!/usr/bin/env python3
"""
Create vouchers for Krankenkassen (Health Insurance) transactions.

This script finds open transactions from health insurance providers
(Techniker Krankenkasse and Knappschaft-Bahn-See) and creates vouchers for them.

Cost Centre: "Lohnnebenkosten" (Payroll Costs)
Accounting Type: "Krankenkasse"

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
from src.vouchers.voucher_utils import find_contact_by_name


# Custom mappings for Krankenkassen script
CONTACT_MAPPINGS = {
    # Map "Knappschaft-Bahn-See" to "Bundesknappschaft Ost"
    'knappschaft-bahn-see': 'Bundesknappschaft Ost',
    'knappschaft': 'Bundesknappschaft Ost',
}


class KrankenkassenVoucherCreator(VoucherCreatorBase):
    """Voucher creator for Krankenkassen (Health Insurance) transactions."""
    
    def __init__(self):
        """Initialize the creator."""
        super().__init__()
        self.cost_centre = None  # Will be loaded in find_accounting_type
    
    def get_script_name(self) -> str:
        """Return script name."""
        return "Krankenkassen"
    
    def get_accounting_type_name(self) -> str:
        """Return accounting type name to search for."""
        return "Krankenkasse"
    
    def find_accounting_type(self, db) -> bool:
        """
        Find accounting type and also load the Lohnnebenkosten cost centre.
        
        Returns:
            True if both found, False otherwise
        """
        # First find the accounting type using parent implementation
        if not super().find_accounting_type(db):
            return False
        
        # Also find the "Lohnnebenkosten" cost centre
        all_cost_centres = db.get_all_cost_centres()
        for cc in all_cost_centres:
            if cc.get('name') == 'Lohnnebenkosten':
                self.cost_centre = cc
                print(f"✓ Found cost centre: {cc['name']} (ID: {cc['id']})")
                print()
                return True
        
        print("Error: Could not find 'Lohnnebenkosten' cost centre!")
        return False
    
    def filter_transactions(self, all_transactions: List[Dict]) -> List[Dict]:
        """Filter transactions from health insurance providers."""
        krankenkassen_transactions = []
        for txn in all_transactions:
            # Parse raw data to get payeePayerName
            raw_data = json.loads(txn.get('raw_data', '{}'))
            payee_name = raw_data.get('payeePayerName', '') or ''
            
            # Match if payee is a known health insurance provider
            if ('Techniker Krankenkasse' in payee_name or 
                'Knappschaft-Bahn-See' in payee_name or
                'Knappschaft' in payee_name or
                'Verwaltungs-Berufsgenossenschaft' in payee_name):
                krankenkassen_transactions.append(txn)
        
        return krankenkassen_transactions
    
    def build_voucher_plan_item(
        self,
        transaction: Dict,
        voucher_number: str,
        index: int
    ) -> Dict:
        """Build voucher plan item for a Krankenkassen transaction."""
        # Parse raw data to get payeePayerName
        raw_data = json.loads(transaction.get('raw_data', '{}'))
        payee_payer_name = raw_data.get('payeePayerName', 'Unknown')
        
        # Find matching contact (health insurance company)
        contact = self._find_krankenkassen_contact(payee_payer_name)
        
        # Extract year and month from transaction date for description
        # Format: YYYYMM (e.g., "202510" for October 2025)
        transaction_date = transaction['value_date'][:10]  # YYYY-MM-DD
        year_month = transaction_date[:7].replace('-', '')  # YYYYMM
        
        return {
            'transaction_id': transaction['id'],
            'transaction_date': transaction['value_date'],
            'amount': transaction['amount'],
            'payment_purpose': transaction['paymt_purpose'],
            'payee_payer_name': payee_payer_name,
            'cost_centre': self.cost_centre,  # Same for all
            'contact': contact,
            'voucher_number': voucher_number,
            'accounting_type': self.accounting_type,
            'description': year_month  # Custom description (e.g., "202510")
        }
    
    def _find_krankenkassen_contact(self, payee_name: str) -> dict:
        """Find contact for Krankenkassen (prefer Suppliers for expenses)."""
        return find_contact_by_name(
            self.db,
            payee_name,
            prefer_category=3,
            custom_mappings=CONTACT_MAPPINGS
        )
    
    def is_income_voucher(self) -> bool:
        """Krankenkassen is an expense."""
        return False


def main():
    """Main function."""
    creator = KrankenkassenVoucherCreator()
    creator.run()


if __name__ == '__main__':
    main()
