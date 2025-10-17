#!/usr/bin/env python3
"""
Create vouchers for Fee transactions (Bank and PayPal fees).

This script finds open transactions with:
1. Name: "Paypal Inc." AND Purpose contains: "Gebühren zu", OR
2. Purpose contains: "Saldo der Abschlussposten QM"

Uses:
- Accounting Type: "Kontoführung / Kartengebühren"
- Cost Centre: "Buchführung, Bankgebühren"
- Contact: Matched by transaction name (e.g., "Paypal Inc." or from transaction)
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


# Cost centre name
COST_CENTRE_NAME = 'Buchführung, Bankgebühren'


class FeesVoucherCreator(VoucherCreatorBase):
    """Voucher creator for Fee transactions (Bank and PayPal fees)."""
    
    def __init__(self):
        """Initialize the creator."""
        super().__init__()
        self.cost_centre_buchfuehrung = None
        self.contact_70000 = None
    
    def get_script_name(self) -> str:
        """Return script name."""
        return "Fees"
    
    def get_accounting_type_name(self) -> str:
        """Return accounting type name to search for."""
        return "Kontoführung / Kartengebühren"
    
    def get_markdown_output_file(self) -> str:
        """Get the output markdown filename."""
        return "voucher_plan_fees.md"
    
    def get_script_filename(self) -> str:
        """Get the script filename for help text."""
        return "create_vouchers_for_fees.py"
    
    def find_accounting_type(self, db) -> bool:
        """
        Find accounting type and also load the cost centre and contact 70000.
        
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
        
        # Find the contact "70000" as fallback for transactions without payee
        self.contact_70000 = find_contact_by_name(db, '70000')
        if not self.contact_70000:
            print(f"Warning: Could not find contact '70000' for fallback!")
        else:
            print(f"✓ Found fallback contact: {self.contact_70000['name']} (ID: {self.contact_70000['id']})")
        
        print()
        return True
    
    def filter_transactions(self, all_transactions: List[Dict]) -> List[Dict]:
        """
        Filter transactions matching fee criteria:
        1. Name: "Paypal Inc." AND Purpose contains: "Gebühren zu", OR
        2. Purpose contains: "Saldo der Abschlussposten QM"
        """
        fee_transactions = []
        for txn in all_transactions:
            # Parse raw data to check payeePayerName
            raw_data = json.loads(txn.get('raw_data', '{}'))
            payee_payer_name = raw_data.get('payeePayerName', '') or ''
            payment_purpose = txn.get('paymt_purpose', '') or ''
            
            # Condition 1: Check for "Paypal Inc." in payeePayerName and "Gebühren zu" in purpose
            is_paypal_inc = 'Paypal Inc.' in payee_payer_name
            has_gebuehren = 'Gebühren zu' in payment_purpose
            is_paypal_fee = is_paypal_inc and has_gebuehren
            
            # Condition 2: Check for "Saldo der Abschlussposten QM" in purpose
            has_saldo_abschluss = 'Saldo der Abschlussposten QM' in payment_purpose
            
            # Add if either condition is met
            if is_paypal_fee or has_saldo_abschluss:
                fee_transactions.append(txn)
        
        return fee_transactions
    
    def build_voucher_plan_item(
        self,
        transaction: Dict,
        voucher_number: str,
        index: int
    ) -> Dict:
        """Build voucher plan item for a fee transaction."""
        # Parse raw data to get payeePayerName
        raw_data = json.loads(transaction.get('raw_data', '{}'))
        payee_payer_name = raw_data.get('payeePayerName', '') or 'Unknown'
        
        # Use the configured cost centre
        cost_centre = self.cost_centre_buchfuehrung
        
        # Find contact by payee/payer name, or use 70000 as fallback if no payee
        if payee_payer_name == 'Unknown' or not payee_payer_name:
            contact = self.contact_70000
        else:
            contact = find_contact_by_name(self.db, payee_payer_name)
            # If contact not found by name, also use 70000 as fallback
            if not contact:
                contact = self.contact_70000
        
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
        Fees are expenses.
        """
        return False
    
    def has_cost_centre(self) -> bool:
        """Fee vouchers use cost centres."""
        return True


def main():
    """Main function."""
    creator = FeesVoucherCreator()
    creator.run()


if __name__ == '__main__':
    main()
