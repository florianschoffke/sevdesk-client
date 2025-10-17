#!/usr/bin/env python3
"""
Create vouchers for Geldtransit (Money Transit) transactions.

This script finds open transactions with:
1. "Bankeinzug" in the payeePayerName, OR
2. "PayPal (Europe) S.a r.l. et Cie, S. C.A." in payeePayerName AND "Ihr Einkauf bei" in purpose

Uses:
- Accounting Type: "Geldtransit"
- Cost Centre: None (no cost centre assignment)
- Contact: "70000" (matched by name)
- Description: Payment purpose from transaction

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


# Contact name for Geldtransit
CONTACT_NAME = '70000'


class GeldtransitVoucherCreator(VoucherCreatorBase):
    """Voucher creator for Geldtransit (Money Transit) transactions."""
    
    def __init__(self):
        """Initialize the creator."""
        super().__init__()
        self.contact_70000 = None  # Will be loaded in find_accounting_type
    
    def get_script_name(self) -> str:
        """Return script name."""
        return "Geldtransit"
    
    def get_accounting_type_name(self) -> str:
        """Return accounting type name to search for."""
        return "Geldtransit"
    
    def get_markdown_output_file(self) -> str:
        """Get the output markdown filename."""
        return "voucher_plan_geldtransit.md"
    
    def get_script_filename(self) -> str:
        """Get the script filename for help text."""
        return "create_vouchers_for_geldtransit.py"
    
    def find_accounting_type(self, db) -> bool:
        """
        Find accounting type and also load the 70000 contact.
        
        Returns:
            True if both found, False otherwise
        """
        # First find the accounting type using parent implementation
        if not super().find_accounting_type(db):
            return False
        
        # Find the contact "70000"
        self.contact_70000 = find_contact_by_name(db, CONTACT_NAME)
        if not self.contact_70000:
            print(f"Error: Could not find contact '{CONTACT_NAME}'!")
            print("\nSearching for similar contacts...")
            all_contacts = db.get_all_contacts()
            for c in all_contacts:
                if '70000' in str(c.get('name', '')) or '70000' in str(c.get('customerNumber', '')):
                    print(f"  - {c.get('name')} (ID: {c.get('id')}, Customer#: {c.get('customerNumber', 'N/A')})")
            return False
        
        print(f"✓ Found contact: {self.contact_70000['name']} (ID: {self.contact_70000['id']})")
        print()
        return True
    
    def filter_transactions(self, all_transactions: List[Dict]) -> List[Dict]:
        """
        Filter transactions matching Geldtransit criteria:
        1. "Bankeinzug" in payeePayerName, OR
        2. "PayPal (Europe) S.a r.l. et Cie, S. C.A." in payeePayerName AND "Ihr Einkauf bei" in purpose
        """
        geldtransit_transactions = []
        for txn in all_transactions:
            # Parse raw data to check payeePayerName
            raw_data = json.loads(txn.get('raw_data', '{}'))
            payee_payer_name = raw_data.get('payeePayerName', '') or ''
            payment_purpose = txn.get('paymt_purpose', '') or ''
            
            # Condition 1: Check for "Bankeinzug" in payeePayerName (case-insensitive)
            is_bankeinzug = 'BANKEINZUG' in payee_payer_name.upper() or 'Bankeinzug' in payee_payer_name
            
            # Condition 2: Check for PayPal with "Ihr Einkauf bei" in purpose
            is_paypal = 'PayPal (Europe) S.a r.l. et Cie, S. C.A.' in payee_payer_name
            has_einkauf = 'Ihr Einkauf bei' in payment_purpose
            is_paypal_purchase = is_paypal and has_einkauf
            
            # Add if either condition is met
            if is_bankeinzug or is_paypal_purchase:
                geldtransit_transactions.append(txn)
        
        return geldtransit_transactions
    
    def build_voucher_plan_item(
        self,
        transaction: Dict,
        voucher_number: str,
        index: int
    ) -> Dict:
        """Build voucher plan item for a Geldtransit transaction."""
        # Parse raw data to get payeePayerName
        raw_data = json.loads(transaction.get('raw_data', '{}'))
        payee_payer_name = raw_data.get('payeePayerName', 'Unknown')
        
        # Use the 70000 contact for all transactions
        contact = self.contact_70000
        
        # Payment purpose will be used as description in voucher position
        payment_purpose = transaction.get('paymt_purpose', '')
        
        return {
            'transaction_id': transaction['id'],
            'transaction_date': transaction['value_date'],
            'amount': transaction['amount'],
            'payment_purpose': payment_purpose,
            'payee_payer_name': payee_payer_name,
            'cost_centre': None,  # No cost centre for Geldtransit
            'contact': contact,
            'voucher_number': voucher_number,
            'accounting_type': self.accounting_type,
            'description': payment_purpose  # Use payment purpose as description
        }
    
    def is_income_voucher(self) -> bool:
        """
        Determine if these are income or expense vouchers.
        Geldtransit can be both, so we check the amount sign.
        """
        # This will be called per transaction, but we need to handle both
        # For now, return True (income) as default - the base class handles sign
        return True
    
    def has_cost_centre(self) -> bool:
        """Geldtransit vouchers do not use cost centres."""
        return False


def main():
    """Main function."""
    creator = GeldtransitVoucherCreator()
    creator.run()


if __name__ == '__main__':
    main()
