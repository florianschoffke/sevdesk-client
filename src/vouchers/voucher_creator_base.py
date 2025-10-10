#!/usr/bin/env python3
"""
Base class for voucher creation scripts.

This module provides a common foundation for all voucher creation scripts,
eliminating code duplication and providing a consistent interface.
"""
import os
import sys
import json
import argparse
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from src.sevdesk.client import SevDeskClient
from src.database.db import TransactionDB
from scripts.loaders.reload_data import reload_all_data
from src.vouchers.voucher_utils import (
    generate_voucher_numbers,
    build_voucher_plan_markdown,
    print_console_summary,
    print_voucher_table,
    create_voucher_for_transaction
)


class VoucherCreatorBase(ABC):
    """
    Abstract base class for voucher creation scripts.
    
    Provides common functionality for:
    - Environment setup
    - Database initialization
    - Transaction filtering
    - Voucher plan generation
    - Voucher creation workflow
    - Status verification
    
    Subclasses must implement:
    - get_script_name(): Return script name (e.g., "Gehalt")
    - get_accounting_type_name(): Return accounting type to search for
    - filter_transactions(): Filter relevant transactions
    - build_voucher_plan_item(): Build a single voucher plan item
    """
    
    def __init__(self):
        """Initialize the voucher creator."""
        self.api_key: Optional[str] = None
        self.api_url: str = 'https://my.sevdesk.de/api/v1'
        self.db_path: str = 'transactions.db'
        self.client: Optional[SevDeskClient] = None
        self.db: Optional[TransactionDB] = None
        self.accounting_type: Optional[Dict] = None
        self.args: Optional[argparse.Namespace] = None
        
    @abstractmethod
    def get_script_name(self) -> str:
        """
        Get the name of this voucher type (e.g., "Gehalt", "ÜLP", "Spenden").
        Used for display purposes.
        """
        pass
    
    @abstractmethod
    def get_accounting_type_name(self) -> str:
        """
        Get the accounting type name to search for.
        Can return a partial name - will search using 'in' operator.
        """
        pass
    
    @abstractmethod
    def filter_transactions(self, all_transactions: List[Dict]) -> List[Dict]:
        """
        Filter transactions to find relevant ones for this voucher type.
        
        Args:
            all_transactions: List of all open transactions
            
        Returns:
            List of filtered transactions
        """
        pass
    
    @abstractmethod
    def build_voucher_plan_item(
        self,
        transaction: Dict,
        voucher_number: str,
        index: int
    ) -> Dict:
        """
        Build a voucher plan item for a single transaction.
        
        Args:
            transaction: Transaction dictionary
            voucher_number: Pre-generated voucher number
            index: Index of this transaction in the list
            
        Returns:
            Voucher plan dictionary with keys:
                - transaction_id
                - transaction_date
                - amount
                - payment_purpose
                - payee_payer_name
                - cost_centre
                - contact
                - voucher_number
                - accounting_type
                - (optional) description: Custom description for voucher
                - (optional) donation_type: For Spenden script
        """
        pass
    
    def get_markdown_output_file(self) -> str:
        """
        Get the output markdown filename.
        Override to customize.
        """
        script_name_lower = self.get_script_name().lower()
        return f"voucher_plan_{script_name_lower}.md"
    
    def get_script_filename(self) -> str:
        """
        Get the script filename for help text.
        Override to customize.
        """
        script_name_lower = self.get_script_name().lower()
        return f"create_vouchers_for_{script_name_lower}.py"
    
    def show_donation_type_column(self) -> bool:
        """
        Whether to show donation type column in output.
        Override in Spenden script.
        """
        return False
    
    def get_extra_markdown_sections(self, voucher_plan: List[Dict]) -> Optional[List[str]]:
        """
        Get additional markdown sections to include in the plan.
        Override to add custom sections (e.g., donation type statistics).
        
        Args:
            voucher_plan: The complete voucher plan
            
        Returns:
            List of markdown lines or None
        """
        return None
    
    def is_income_voucher(self) -> bool:
        """
        Whether this voucher type represents income (True) or expenses (False).
        Override in income scripts (e.g., Spenden).
        """
        return False
    
    def setup_argument_parser(self) -> argparse.ArgumentParser:
        """
        Setup and return the argument parser.
        Override to add custom arguments.
        """
        parser = argparse.ArgumentParser(
            description=f'Create vouchers for {self.get_script_name()} transactions'
        )
        parser.add_argument(
            '--create-single',
            action='store_true',
            help='Create a single voucher (for testing)'
        )
        parser.add_argument(
            '--create-all',
            action='store_true',
            help='Create all vouchers'
        )
        return parser
    
    def load_environment(self):
        """Load environment variables and validate."""
        load_dotenv()
        
        self.api_key = os.getenv('SEVDESK_API_KEY')
        self.api_url = os.getenv('SEVDESK_API_URL', 'https://my.sevdesk.de/api/v1')
        self.db_path = os.getenv('DB_PATH', 'transactions.db')
        
        if not self.api_key:
            print("Error: SEVDESK_API_KEY not found in environment variables.")
            sys.exit(1)
    
    def print_header(self):
        """Print script header."""
        print("=" * 80)
        print(f"{self.get_script_name()} Voucher Creator")
        print("=" * 80)
        print()
    
    def reload_data(self) -> bool:
        """Reload all data from SevDesk API."""
        print("Reloading all data from SevDesk API...")
        print()
        if not reload_all_data(db_path=self.db_path, api_key=self.api_key, api_url=self.api_url):
            print("Error: Failed to reload data from API")
            return False
        print()
        print("=" * 80)
        print()
        return True
    
    def initialize_api_client(self):
        """Initialize the SevDesk API client."""
        print(f"Connecting to SevDesk API at {self.api_url}...")
        self.client = SevDeskClient(api_key=self.api_key, base_url=self.api_url)
        print("✓ Connected")
        print()
    
    def open_database(self) -> TransactionDB:
        """Open database connection."""
        print(f"Opening database: {self.db_path}")
        return TransactionDB(db_path=self.db_path)
    
    def find_accounting_type(self, db: TransactionDB) -> bool:
        """
        Find the required accounting type.
        
        Returns:
            True if found, False otherwise
        """
        accounting_type_name = self.get_accounting_type_name()
        all_accounting_types = db.get_all_accounting_types()
        
        for at in all_accounting_types:
            if accounting_type_name in at.get('name', ''):
                self.accounting_type = at
                print(f"✓ Found accounting type: {at['name']} (ID: {at['id']})")
                print()
                return True
        
        print(f"Error: Could not find accounting type containing '{accounting_type_name}'!")
        print("\nSearching for similar accounting types...")
        search_terms = accounting_type_name.lower().split()
        for at in all_accounting_types:
            name = at.get('name', '').lower()
            if any(term in name for term in search_terms):
                print(f"  - {at.get('name')} (ID: {at.get('id')})")
        return False
    
    def get_open_transactions(self, db: TransactionDB) -> List[Dict]:
        """Get all open transactions from database."""
        print("Fetching open transactions...")
        all_transactions = db.get_all_transactions(status=100)
        print(f"✓ Found {len(all_transactions)} open transactions")
        print()
        return all_transactions
    
    def generate_voucher_plan(
        self,
        filtered_transactions: List[Dict]
    ) -> List[Dict]:
        """
        Generate voucher plan from filtered transactions.
        
        Args:
            filtered_transactions: List of filtered transactions
            
        Returns:
            List of voucher plan items
        """
        if not filtered_transactions:
            print("No matching transactions found. Exiting.")
            return []
        
        # Generate voucher numbers
        print("Generating voucher numbers...")
        voucher_numbers = generate_voucher_numbers(self.client, len(filtered_transactions))
        print(f"✓ Generated {len(voucher_numbers)} voucher numbers (starting: {voucher_numbers[0]})")
        print()
        
        # Build voucher plan
        voucher_plan = []
        for i, txn in enumerate(filtered_transactions):
            plan_item = self.build_voucher_plan_item(
                transaction=txn,
                voucher_number=voucher_numbers[i],
                index=i
            )
            voucher_plan.append(plan_item)
        
        return voucher_plan
    
    def save_voucher_plan_markdown(self, voucher_plan: List[Dict]) -> str:
        """
        Save voucher plan to markdown file.
        
        Returns:
            Output filename
        """
        extra_sections = self.get_extra_markdown_sections(voucher_plan)
        
        markdown_lines = build_voucher_plan_markdown(
            title=f"{self.get_script_name()} Voucher Plan",
            voucher_plan=voucher_plan,
            accounting_type=self.accounting_type,
            extra_sections=extra_sections,
            show_donation_type=self.show_donation_type_column()
        )
        
        output_file = self.get_markdown_output_file()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_lines))
        
        return output_file
    
    def print_plan_summary(self, voucher_plan: List[Dict], output_file: str):
        """Print summary of the voucher plan."""
        missing_cost_centres = [p for p in voucher_plan if not p.get('cost_centre')]
        missing_contacts = [p for p in voucher_plan if not p.get('contact')]
        
        print_console_summary(
            title=f"{self.get_script_name()} Voucher Creator",
            output_file=output_file,
            voucher_count=len(voucher_plan),
            accounting_type=self.accounting_type,
            missing_cost_centres=len(missing_cost_centres),
            missing_contacts=len(missing_contacts),
            script_name=self.get_script_filename()
        )
        
        if missing_cost_centres:
            print(f"⚠️  WARNING: {len(missing_cost_centres)} transaction(s) have no matching cost centre")
            print("   See the markdown file for details.")
            print()
        
        if missing_contacts:
            print(f"⚠️  WARNING: {len(missing_contacts)} transaction(s) have no matching contact")
            print("   See the markdown file for details.")
            print()
        
        print("Accounting Type for all positions:")
        print(f"  → {self.accounting_type['name']} (ID: {self.accounting_type['id']})")
        print()
        print("Next steps:")
        print(f"  1. Open and review: {output_file}")
        print(f"  2. Test with single voucher: python {self.get_script_filename()} --create-single")
        print(f"  3. Create all vouchers: python {self.get_script_filename()} --create-all")
        print()
        print("=" * 80)
    
    def confirm_creation(self, voucher_plan: List[Dict]) -> bool:
        """
        Show plan and ask for confirmation.
        
        Returns:
            True if user confirmed, False otherwise
        """
        print("=" * 80)
        print("VOUCHER PLAN REVIEW")
        print("=" * 80)
        print()
        print(f"📄 Plan file: {self.get_markdown_output_file()}")
        print()
        
        # Display the plan in a table format
        print_voucher_table(
            voucher_plan=voucher_plan,
            create_all=self.args.create_all,
            show_donation_type=self.show_donation_type_column()
        )
        print(f"Total: {len(voucher_plan) if self.args.create_all else 1} voucher(s) will be created")
        print()
        
        # Ask for confirmation
        print("⚠️  Please review the voucher plan above carefully!")
        print()
        response = input("Do you want to proceed with creating these vouchers? (y/N): ").strip().lower()
        
        if response != 'y':
            print()
            print("❌ Cancelled by user. No vouchers were created.")
            print()
            print("=" * 80)
            return False
        
        print()
        return True
    
    def create_vouchers(
        self,
        voucher_plan: List[Dict],
        check_account_id: str,
        sev_client_id: str
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Create vouchers according to plan.
        
        Args:
            voucher_plan: List of voucher plan items
            check_account_id: Check account ID from transaction
            sev_client_id: SevClient ID from transaction
            
        Returns:
            Tuple of (created_vouchers, failed_vouchers)
        """
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
        is_income = self.is_income_voucher()
        
        for i, plan in enumerate(vouchers_to_create, 1):
            print(f"[{i}/{len(vouchers_to_create)}] Creating voucher for transaction {plan['transaction_id']}...")
            print(f"    Amount: €{plan['amount']:,.2f}")
            print(f"    Payee/Payer: {plan['payee_payer_name']}")
            if plan.get('cost_centre'):
                print(f"    Cost Centre: {plan['cost_centre']['name']}")
            if plan.get('contact'):
                print(f"    Contact: {plan['contact']['name']}")
            
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
    
    def print_creation_summary(
        self,
        created_vouchers: List[Dict],
        failed_vouchers: List[Dict]
    ):
        """Print summary of voucher creation."""
        print("=" * 80)
        print("CREATION SUMMARY")
        print("=" * 80)
        print()
        print(f"✓ Successfully created: {len(created_vouchers)} voucher(s)")
        if failed_vouchers:
            print(f"❌ Failed: {len(failed_vouchers)} voucher(s)")
        print()
    
    def verify_transaction_statuses(self, created_vouchers: List[Dict]):
        """Verify that transactions have been updated after voucher creation."""
        if not created_vouchers:
            return
        
        print("Verifying transaction statuses...")
        print()
        
        # Reload transactions from API
        print("Reloading transactions from API...")
        try:
            updated_transactions = self.client.get_all_transactions(status=None)
            print(f"✓ Loaded {len(updated_transactions)} transactions")
            print()
            
            # Check each created voucher's transaction
            for created in created_vouchers:
                txn_id = created['plan']['transaction_id']
                txn = next((t for t in updated_transactions if t.get('id') == txn_id), None)
                
                if txn:
                    old_status = 100  # Was open
                    new_status = txn.get('status')
                    status_name = {100: 'Open', 200: 'Linked', 1000: 'Booked'}.get(new_status, f'Unknown ({new_status})')
                    
                    if new_status != old_status:
                        print(f"✓ Transaction {txn_id}: {old_status} → {new_status} ({status_name})")
                    else:
                        print(f"⚠️  Transaction {txn_id}: Still at status {new_status} ({status_name})")
                else:
                    print(f"❌ Transaction {txn_id}: Not found in updated data")
            
            print()
            
            # Update database
            print("Updating local database...")
            with TransactionDB(db_path=self.db_path) as db_update:
                inserted = db_update.bulk_insert_transactions(updated_transactions)
                print(f"✓ Updated {inserted} transactions in database")
            print()
            
        except Exception as e:
            print(f"❌ Error during verification: {str(e)}")
            print()
    
    def print_footer(self):
        """Print script footer."""
        print("=" * 80)
        print("DONE")
        print("=" * 80)
    
    def run(self):
        """
        Main execution flow.
        This is the entry point that orchestrates the entire process.
        """
        # Setup
        parser = self.setup_argument_parser()
        self.args = parser.parse_args()
        
        self.load_environment()
        self.print_header()
        
        # Reload data
        if not self.reload_data():
            sys.exit(1)
        
        # Initialize API client
        self.initialize_api_client()
        
        # Open database and process
        with self.open_database() as db:
            self.db = db
            
            # Find accounting type
            if not self.find_accounting_type(db):
                sys.exit(1)
            
            # Get and filter transactions
            all_transactions = self.get_open_transactions(db)
            filtered_transactions = self.filter_transactions(all_transactions)
            
            if not filtered_transactions:
                print("No matching transactions found. Exiting.")
                return
            
            print(f"✓ Found {len(filtered_transactions)} matching transactions")
            print()
            
            # Generate voucher plan
            voucher_plan = self.generate_voucher_plan(filtered_transactions)
            if not voucher_plan:
                return
            
            # Save markdown plan
            output_file = self.save_voucher_plan_markdown(voucher_plan)
            
            # If no create flag, just show the plan
            if not self.args.create_single and not self.args.create_all:
                self.print_plan_summary(voucher_plan, output_file)
                return
            
            # Show plan and confirm
            if not self.confirm_creation(voucher_plan):
                return
            
            # Get check account and sev client IDs from first transaction
            first_txn_raw = json.loads(filtered_transactions[0].get('raw_data', '{}'))
            check_account_id = first_txn_raw.get('checkAccount', {}).get('id')
            sev_client_id = first_txn_raw.get('sevClient', {}).get('id')
            
            # Create vouchers
            created_vouchers, failed_vouchers = self.create_vouchers(
                voucher_plan,
                check_account_id,
                sev_client_id
            )
            
            # Print summary
            self.print_creation_summary(created_vouchers, failed_vouchers)
            
            # Verify transaction statuses
            self.verify_transaction_statuses(created_vouchers)
            
            # Done
            self.print_footer()
