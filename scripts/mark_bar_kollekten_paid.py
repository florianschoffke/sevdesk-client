#!/usr/bin/env python3
"""
Mark Bar-Kollekten vouchers as paid.

This script finds open income vouchers with cost centre "Bar-Kollekten"
and marks them as paid with the payment date set to the voucher date,
assigned to the "Kasse" check account.

Usage:
    python3 mark_bar_kollekten_paid.py              # Show overview
    python3 mark_bar_kollekten_paid.py --mark-single # Mark one voucher as test
    python3 mark_bar_kollekten_paid.py --mark-all    # Mark all vouchers
"""
import os
import sys
import argparse
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.sevdesk.client import SevDeskClient
from src.database.db import TransactionDB


# Check account ID for "Kasse"
KASSE_CHECK_ACCOUNT_ID = '5472950'

# Cost centre names to filter (all Bar-Kollekten related)
COST_CENTRE_NAMES = ['Bar-Kollekten', 'Bar-Kollekten Missionare']


class BarKollektenMarker:
    """Mark Bar-Kollekten vouchers as paid."""
    
    def __init__(self):
        """Initialize the marker."""
        self.api_key = None
        self.api_url = 'https://my.sevdesk.de/api/v1'
        self.db_path = 'transactions.db'
        self.client = None
        self.db = None
        
    def load_environment(self):
        """Load environment variables."""
        load_dotenv()
        self.api_key = os.getenv('SEVDESK_API_KEY')
        if not self.api_key:
            print("Error: SEVDESK_API_KEY not found in environment")
            print("Please set it in .env file")
            sys.exit(1)
    
    def initialize_api_client(self):
        """Initialize the SevDesk API client."""
        print(f"Connecting to SevDesk API at {self.api_url}...")
        self.client = SevDeskClient(api_key=self.api_key, base_url=self.api_url)
        print("✓ Connected")
        print()
    
    def open_database(self):
        """Open database connection."""
        print(f"Opening database: {self.db_path}")
        self.db = TransactionDB(db_path=self.db_path)
        print("✓ Database opened")
        print()
    
    def get_bar_kollekten_cost_centre_ids(self) -> List[str]:
        """Get all Bar-Kollekten related cost centre IDs."""
        all_cost_centres = self.db.get_all_cost_centres()
        ids = []
        for cc in all_cost_centres:
            if cc.get('name') in COST_CENTRE_NAMES:
                ids.append(str(cc.get('id')))
        return ids
    
    def get_open_bar_kollekten_vouchers(self):
        """
        Get all Bar-Kollekten income vouchers that need payment recording.
        
        This only includes Status 100 (Paid) vouchers with paidAmount=0.
        These are vouchers that were manually marked as paid but don't have 
        the payment transaction recorded.
        
        Status 50 (Unpaid) vouchers are excluded as they should remain unpaid.
        
        Includes vouchers from:
        - Bar-Kollekten
        - Bar-Kollekten Missionare
        
        Returns:
            List of voucher dictionaries
        """
        # Get Bar-Kollekten cost centre IDs from database
        cost_centres = self.db.get_all_cost_centres()
        bar_kollekten_ids = []
        for cc in cost_centres:
            if cc.get('name') in COST_CENTRE_NAMES:
                bar_kollekten_ids.append(str(cc.get('id')))
        
        if not bar_kollekten_ids:
            print("❌ Error: Could not find any Bar-Kollekten cost centres")
            return []
        
        print(f"📊 Found Bar-Kollekten cost centres: {', '.join(COST_CENTRE_NAMES)}")
        print(f"   Cost centre IDs: {', '.join(bar_kollekten_ids)}")
        
        matching_vouchers = []
        
        # Get paid vouchers with paidAmount=0 (status=100 but payment not recorded)
        print("🔍 Checking paid vouchers without payment record (status=100, paidAmount=0)...")
        params = {'status': 100, 'limit': 1000}
        response = self.client._request('GET', '/Voucher', params=params)
        
        if response and 'objects' in response:
            for voucher in response['objects']:
                cost_centre = voucher.get('costCentre')
                credit_debit = voucher.get('creditDebit')
                paid_amount = voucher.get('paidAmount', 0)
                
                if (cost_centre and 
                    str(cost_centre.get('id')) in bar_kollekten_ids and 
                    credit_debit == 'D' and  # D = Debit = Income
                    paid_amount == 0):  # Payment not recorded
                    matching_vouchers.append(voucher)
            
            print(f"  Found {len(matching_vouchers)} paid vouchers without payment record")
        
        print(f"✅ Total: {len(matching_vouchers)} Bar-Kollekten income vouchers need payment recording")
        print(f"ℹ️  Note: Status 50 (Unpaid) vouchers are excluded")
        return matching_vouchers
    
    def get_voucher_details(self, voucher_id: str) -> Dict:
        """Get full voucher details including positions."""
        response = self.client._request('GET', f'/Voucher/{voucher_id}')
        if response and 'objects' in response and len(response['objects']) > 0:
            return response['objects'][0]
        return None
    
    def build_markdown_table(self, vouchers: List[Dict]) -> str:
        """
        Build a markdown table of vouchers to be marked as paid.
        
        Args:
            vouchers: List of voucher dictionaries
            
        Returns:
            Markdown formatted table as string
        """
        if not vouchers:
            return "No Bar-Kollekten vouchers to mark as paid.\n"
        
        lines = []
        lines.append("| # | Voucher ID | Date | Amount | Description |")
        lines.append("|---|------------|------|--------|-------------|")
        
        total_amount = 0
        for i, voucher in enumerate(vouchers, 1):
            voucher_id = voucher.get('id')
            voucher_date = voucher.get('voucherDate', '')[:10]
            
            # Get full voucher details to get sumNet
            full_voucher = self.get_voucher_details(voucher_id)
            if full_voucher:
                amount = float(full_voucher.get('sumNet', 0))
                total_amount += amount
            else:
                amount = 0
            
            description = voucher.get('description', '')[:40]
            
            lines.append(f"| {i} | {voucher_id} | {voucher_date} | €{amount:,.2f} | {description} |")
        
        lines.append("")
        lines.append(f"**Total: {len(vouchers)} voucher(s) - €{total_amount:,.2f}**")
        lines.append("")
        
        return "\n".join(lines)
    
    def print_vouchers_overview(self, vouchers: List[Dict]):
        """Print overview of vouchers to be marked."""
        if not vouchers:
            print("\nNo vouchers to process.")
            return
        
        print("\n" + "=" * 100)
        print("BAR-KOLLEKTEN VOUCHERS TO MARK AS PAID")
        print("=" * 100)
        print()
        print(f"{'#':<4} {'Voucher ID':<12} {'Date':<12} {'Amount':<12} {'Description':<40}")
        print("-" * 100)
        
        for i, voucher in enumerate(vouchers, 1):
            voucher_id = voucher.get('id')
            voucher_date = voucher.get('voucherDate', '')[:10]
            
            # Use sumNet from the voucher object (no need to fetch full details)
            amount = float(voucher.get('sumNet', 0))
            
            description = voucher.get('description', '')[:40]
            
            print(f"{i:<4} {voucher_id:<12} {voucher_date:<12} €{amount:>9,.2f}   {description:<40}")
        
        print()
        print(f"Total: {len(vouchers)} voucher(s)")
        print()
    
    def mark_voucher_as_paid(self, voucher: Dict) -> bool:
        """
        Mark a single voucher as paid.
        
        Args:
            voucher: Voucher dictionary
            
        Returns:
            True if successful, False otherwise
        """
        voucher_id = voucher.get('id')
        voucher_date = voucher.get('voucherDate', '')[:10]
        
        # Get full voucher details to get the correct amount
        full_voucher = self.get_voucher_details(voucher_id)
        if full_voucher:
            amount = float(full_voucher.get('sumNet', 0))
        else:
            amount = 0
        
        print(f"  Marking voucher {voucher_id} as paid...")
        print(f"    Date: {voucher_date}")
        print(f"    Amount: €{amount:,.2f}")
        print(f"    Account: Kasse (ID: {KASSE_CHECK_ACCOUNT_ID})")
        
        try:
            # Book the voucher amount
            # For income vouchers, we need to book with positive amount
            # The date is the voucher date (payment date = voucher date for Bar-Kollekten)
            data = {
                'amount': abs(amount),  # Positive for income
                'date': voucher_date,
                'type': 'N',  # Normal payment
                'checkAccount': {
                    'id': KASSE_CHECK_ACCOUNT_ID,
                    'objectName': 'CheckAccount'
                },
                'createFeed': True
            }
            
            response = self.client._request('PUT', f'/Voucher/{voucher_id}/bookAmount', data=data)
            
            if response:
                print(f"  ✓ Successfully marked voucher {voucher_id} as paid")
                return True
            else:
                print(f"  ✗ Failed to mark voucher {voucher_id} as paid")
                return False
                
        except Exception as e:
            print(f"  ✗ Error marking voucher {voucher_id}: {e}")
            return False
    
    def confirm_marking(self, vouchers: List[Dict], mark_all: bool) -> bool:
        """
        Ask for confirmation before marking vouchers.
        
        Returns:
            True if user confirmed, False otherwise
        """
        if not vouchers:
            return False
        
        count = len(vouchers) if mark_all else 1
        print("=" * 100)
        print("CONFIRMATION")
        print("=" * 100)
        print()
        print(f"You are about to mark {count} voucher(s) as paid.")
        print(f"Payment account: Kasse (ID: {KASSE_CHECK_ACCOUNT_ID})")
        print(f"Payment dates: Voucher dates (as shown above)")
        print()
        print("⚠️  This action cannot be easily undone!")
        print()
        response = input(f"Do you want to proceed? (y/N): ").strip().lower()
        
        return response == 'y'
    
    def generate_report(self, vouchers: List[Dict], output_file: str = 'reports/bar_kollekten_to_mark.md'):
        """
        Generate markdown report of vouchers to be marked.
        
        Args:
            vouchers: List of voucher dictionaries
            output_file: Output file path
        """
        # Build markdown content
        content = []
        content.append("# Bar-Kollekten Vouchers to Mark as Paid\n")
        content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        content.append("")
        content.append("These vouchers need to be marked as paid to the **Kasse** (cash register) account.\n")
        content.append("")
        
        # Add table
        content.append(self.build_markdown_table(vouchers))
        
        # Write to file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        print(f"📄 Report saved to: {output_file}")
    
    def run(self, mark_single: bool = False, mark_all: bool = False, generate_report: bool = True):
        """
        Main execution flow.
        
        Args:
            mark_single: If True, mark only the first voucher as test
            mark_all: If True, mark all vouchers
            generate_report: If True, generate markdown report
        """
        print("=" * 100)
        print("BAR-KOLLEKTEN VOUCHER MARKER")
        print("=" * 100)
        print()
        
        # Setup
        self.load_environment()
        self.initialize_api_client()
        self.open_database()
        
        # Get vouchers
        vouchers = self.get_open_bar_kollekten_vouchers()
        
        # Print overview
        self.print_vouchers_overview(vouchers)
        
        # Generate report
        if generate_report:
            self.generate_report(vouchers)
            print()
        
        # If no action requested, just show overview
        if not mark_single and not mark_all:
            print("=" * 100)
            print("OVERVIEW MODE")
            print("=" * 100)
            print()
            print("To mark vouchers as paid:")
            print("  - Test with single voucher: python3 mark_bar_kollekten_paid.py --mark-single")
            print("  - Mark all vouchers:        python3 mark_bar_kollekten_paid.py --mark-all")
            print()
            return
        
        # Confirm before proceeding
        if not self.confirm_marking(vouchers, mark_all):
            print("\n❌ Marking cancelled by user")
            return
        
        # Mark vouchers
        print("\n" + "=" * 100)
        print("MARKING VOUCHERS AS PAID")
        print("=" * 100)
        print()
        
        vouchers_to_mark = vouchers if mark_all else [vouchers[0]]
        success_count = 0
        fail_count = 0
        
        for voucher in vouchers_to_mark:
            if self.mark_voucher_as_paid(voucher):
                success_count += 1
            else:
                fail_count += 1
            print()
        
        # Summary
        print("=" * 100)
        print("SUMMARY")
        print("=" * 100)
        print()
        print(f"✓ Successfully marked: {success_count}")
        if fail_count > 0:
            print(f"✗ Failed: {fail_count}")
        print()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Mark Bar-Kollekten vouchers as paid'
    )
    parser.add_argument(
        '--mark-single',
        action='store_true',
        help='Mark only the first voucher as test'
    )
    parser.add_argument(
        '--mark-all',
        action='store_true',
        help='Mark all vouchers as paid'
    )
    
    args = parser.parse_args()
    
    marker = BarKollektenMarker()
    marker.run(mark_single=args.mark_single, mark_all=args.mark_all)


if __name__ == '__main__':
    main()
