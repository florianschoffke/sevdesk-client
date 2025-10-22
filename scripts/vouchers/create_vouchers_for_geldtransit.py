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
        Geldtransit can be both, so we need to check per transaction.
        """
        # This method is called by the base class, but it doesn't have access
        # to individual transaction data. We need to override the voucher creation
        # to handle this per transaction.
        return True  # Default, will be overridden in voucher creation
    
    def has_cost_centre(self) -> bool:
        """Geldtransit vouchers do not use cost centres."""
        return False
    
    def _is_paypal_fee_transaction(self, plan: Dict) -> bool:
        """
        Determine if this is a PayPal fee transaction (expense).
        
        Args:
            plan: Voucher plan item
            
        Returns:
            True if this is a PayPal fee, False otherwise
        """
        payee_name = plan.get('payee_payer_name', '')
        return 'PayPal (Europe) S.a r.l. et Cie, S. C.A.' in payee_name
    
    def create_vouchers(
        self,
        voucher_plan: List[Dict],
        check_account_id: str,
        sev_client_id: str
    ) -> tuple:
        """
        Override to handle income vs expense determination per transaction.
        """
        from src.vouchers.voucher_utils import create_voucher_for_transaction
        
        print("=" * 80)
        print("CREATING VOUCHERS")
        print("=" * 80)
        print()
        
        # Determine which vouchers to create
        vouchers_to_create = [voucher_plan[0]] if self.args.create_single else voucher_plan
        
        print(f"Creating {len(vouchers_to_create)} voucher(s)...")
        print()
        
        created_vouchers = []
        failed_vouchers = []
        
        for i, plan in enumerate(vouchers_to_create, 1):
            print(f"[{i}/{len(vouchers_to_create)}] Creating voucher for transaction {plan['transaction_id']}...")
            print(f"    Amount: €{plan['amount']:,.2f}")
            print(f"    Payee/Payer: {plan['payee_payer_name']}")
            if plan.get('cost_centre'):
                print(f"    Cost Centre: {plan['cost_centre']['name']}")
            if plan.get('contact'):
                print(f"    Contact: {plan['contact']['name']}")
            
            # Determine if this is income or expense per transaction
            is_paypal_fee = self._is_paypal_fee_transaction(plan)
            is_income = not is_paypal_fee  # PayPal fees are expenses, others are income
            
            print(f"    Type: {'Expense' if not is_income else 'Income'}")
            
            try:
                response = create_voucher_for_transaction(
                    self.client,
                    plan,
                    check_account_id,
                    sev_client_id,
                    is_income=is_income
                )
                
                if response and 'objects' in response:
                    # Extract voucher ID from nested structure
                    voucher_id = response['objects'].get('voucher', {}).get('id')
                    print(f"    ✓ Voucher created successfully! ID: {voucher_id}")
                    
                    # Book voucher amount to link it to the transaction
                    print(f"    Booking voucher amount to link to transaction...")
                    try:
                        book_response = self.client.book_voucher_amount(
                            voucher_id=voucher_id,
                            transaction_id=plan['transaction_id'],
                            check_account_id=check_account_id,
                            amount=plan['amount'],
                            date=plan['transaction_date'][:10],
                            is_income=is_income
                        )
                        print(f"    ✓ Voucher booked and linked to transaction!")
                    except Exception as link_error:
                        print(f"    ⚠️  Warning: Failed to book/link voucher: {str(link_error)}")
                    
                    created_vouchers.append({
                        'plan': plan,
                        'voucher_id': voucher_id,
                        'response': response
                    })
                else:
                    print(f"    ❌ Failed: Unexpected response format")
                    failed_vouchers.append(plan)
                    
            except Exception as e:
                print(f"    ❌ Failed: {str(e)}")
                failed_vouchers.append(plan)
            
            print()
        
        return created_vouchers, failed_vouchers


def main():
    """Main function."""
    creator = GeldtransitVoucherCreator()
    creator.run()


if __name__ == '__main__':
    main()
