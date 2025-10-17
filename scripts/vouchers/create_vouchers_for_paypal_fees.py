#!/usr/bin/env python3
"""
Create vouchers for PayPal Fee transactions.

This script finds open transactions with:
- Name: "Paypal Inc."
- Purpose contains: "Gebühren zu"

Uses:
- Accounting Type: "Kontoführung / Kartengebühren"
- Cost Centre: "Buchführung, Bankgebühren"
- Contact: Matched by name "Paypal Inc."
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
from src.vouchers.voucher_utils import find_cost_centre_by_name, find_contact_by_name


# Cost centre and contact names
COST_CENTRE_NAME = 'Buchführung, Bankgebühren'
CONTACT_NAME = 'Paypal Inc.'


class PayPalFeesVoucherCreator(VoucherCreatorBase):
    """Voucher creator for PayPal Fee transactions."""
    
    def __init__(self):
        """Initialize the creator."""
        super().__init__()
        self.cost_centre_buchfuehrung = None
        self.contact_paypal = None
    
    def get_script_name(self) -> str:
        """Return script name."""
        return "PayPal Fees"
    
    def get_accounting_type_name(self) -> str:
        """Return accounting type name to search for."""
        return "Kontoführung / Kartengebühren"
    
    def get_markdown_output_file(self) -> str:
        """Get the output markdown filename."""
        return "voucher_plan_paypal_fees.md"
    
    def get_script_filename(self) -> str:
        """Get the script filename for help text."""
        return "create_vouchers_for_paypal_fees.py"
    
    def find_accounting_type(self, db) -> bool:
        """
        Find accounting type and also load the cost centre and contact.
        
        Returns:
            True if all found, False otherwise
        """
        # First find the accounting type using parent implementation
        if not super().find_accounting_type(db):
            return False
        
        # Find the cost centre "Buchführung, Bankgebühren"
        self.cost_centre_buchfuehrung = find_cost_centre_by_name(db, COST_CENTRE_NAME)
        if not self.cost_centre_buchfuehrung:
            print(f"Error: Could not find cost centre '{COST_CENTRE_NAME}'!")
            print("\nSearching for similar cost centres...")
            all_cost_centres = db.get_all_cost_centres()
            for cc in all_cost_centres:
                if 'Buchführung' in str(cc.get('name', '')) or 'Bankgebühren' in str(cc.get('name', '')):
                    print(f"  - {cc.get('name')} (ID: {cc.get('id')})")
            return False
        
        print(f"✓ Found cost centre: {self.cost_centre_buchfuehrung['name']} (ID: {self.cost_centre_buchfuehrung['id']})")
        
        # Find the contact "Paypal Inc."
        self.contact_paypal = find_contact_by_name(db, CONTACT_NAME)
        if not self.contact_paypal:
            print(f"Error: Could not find contact '{CONTACT_NAME}'!")
            print("\nSearching for similar contacts...")
            all_contacts = db.get_all_contacts()
            for c in all_contacts:
                if 'paypal' in str(c.get('name', '')).lower():
                    print(f"  - {c.get('name')} (ID: {c.get('id')})")
            return False
        
        print(f"✓ Found contact: {self.contact_paypal['name']} (ID: {self.contact_paypal['id']})")
        print()
        return True
    
    def filter_transactions(self, all_transactions: List[Dict]) -> List[Dict]:
        """
        Filter transactions matching PayPal fee criteria:
        - Name: "Paypal Inc."
        - Purpose contains: "Gebühren zu"
        """
        paypal_fee_transactions = []
        for txn in all_transactions:
            # Parse raw data to check payeePayerName
            raw_data = json.loads(txn.get('raw_data', '{}'))
            payee_payer_name = raw_data.get('payeePayerName', '') or ''
            payment_purpose = txn.get('paymt_purpose', '') or ''
            
            # Check for "Paypal Inc." in payeePayerName and "Gebühren zu" in purpose
            is_paypal_inc = 'Paypal Inc.' in payee_payer_name
            has_gebuehren = 'Gebühren zu' in payment_purpose
            
            # Add if both conditions are met
            if is_paypal_inc and has_gebuehren:
                paypal_fee_transactions.append(txn)
        
        return paypal_fee_transactions
    
    def build_voucher_plan_item(
        self,
        transaction: Dict,
        voucher_number: str,
        index: int
    ) -> Dict:
        """Build voucher plan item for a PayPal fee transaction."""
        # Parse raw data to get payeePayerName
        raw_data = json.loads(transaction.get('raw_data', '{}'))
        payee_payer_name = raw_data.get('payeePayerName', 'Unknown')
        
        # Use the configured cost centre and contact
        cost_centre = self.cost_centre_buchfuehrung
        contact = self.contact_paypal
        
        # Payment purpose will be used as description in voucher position
        payment_purpose = transaction.get('paymt_purpose', '')
        
        return {
            'transaction_id': transaction['id'],
            'transaction_date': transaction['value_date'],
            'amount': transaction['amount'],
            'payment_purpose': payment_purpose,
            'payee_payer_name': payee_payer_name,
            'cost_centre': cost_centre,
            'contact': contact,
            'voucher_number': voucher_number,
            'accounting_type': self.accounting_type,
            'description': payment_purpose  # Use payment purpose as description
        }
    
    def is_income_voucher(self) -> bool:
        """
        Determine if these are income or expense vouchers.
        PayPal fees are expenses.
        """
        return False
    
    def has_cost_centre(self) -> bool:
        """PayPal fee vouchers use cost centres."""
        return True


def main():
    """Main function."""
    creator = PayPalFeesVoucherCreator()
    creator.run()


if __name__ == '__main__':
    main()
