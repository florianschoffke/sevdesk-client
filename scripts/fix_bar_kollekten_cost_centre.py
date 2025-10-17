#!/usr/bin/env python3
"""
Fix Bar-Kollekten Vouchers - Assign Cost Centre and Update Accounting Type

This script finds income vouchers (status=100, paidAmount=0, creditDebit=D) 
without a cost centre and:
1. Assigns them to the "Bar-Kollekten" cost centre (ID: 180758)
2. Changes the accounting type from "Bar-Kollekte" to "Spendeneingang" (ID: 935667)

Usage:
    python3 fix_bar_kollekten_cost_centre.py          # List vouchers that need fixing
    python3 fix_bar_kollekten_cost_centre.py --fix-single  # Fix one voucher as test
    python3 fix_bar_kollekten_cost_centre.py --fix-all     # Fix all vouchers
"""

import sys
import os
from typing import List, Dict
from dotenv import load_dotenv
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from sevdesk.client import SevDeskClient
from database.db import TransactionDB


# Constants
BAR_KOLLEKTEN_COST_CENTRE_ID = '180758'  # Bar-Kollekten
BAR_KOLLEKTEN_COST_CENTRE_NAME = 'Bar-Kollekten'
SPENDENEINGANG_ACCOUNTING_TYPE_ID = '935667'  # Spendeneingang
SPENDENEINGANG_ACCOUNTING_TYPE_NAME = 'Spendeneingang'


class BarKollektenFixer:
    """Fix Bar-Kollekten vouchers by assigning cost centre."""
    
    def __init__(self):
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
        self.db = TransactionDB(self.db_path)
        print("✓ Database opened")
        print()
    
    def get_vouchers_without_cost_centre(self) -> List[Dict]:
        """
        Get all income vouchers without cost centre.
        
        Returns:
            List of voucher dictionaries
        """
        print("🔍 Finding income vouchers without cost centre...")
        print("   Criteria: status=100 (Paid), paidAmount=0, creditDebit=D (Income)")
        print()
        
        matching_vouchers = []
        
        # Get paid vouchers with paidAmount=0
        params = {'status': 100, 'limit': 1000}
        response = self.client._request('GET', '/Voucher', params=params)
        
        if response and 'objects' in response:
            for voucher in response['objects']:
                cost_centre = voucher.get('costCentre')
                credit_debit = voucher.get('creditDebit')
                paid_amount = voucher.get('paidAmount', 0)
                
                if (not cost_centre and 
                    credit_debit == 'D' and  # D = Debit = Income
                    paid_amount == 0):  # Payment not recorded
                    matching_vouchers.append(voucher)
        
        print(f"✅ Found {len(matching_vouchers)} voucher(s) without cost centre")
        return matching_vouchers
    
    def print_vouchers_overview(self, vouchers: List[Dict]):
        """Print overview of vouchers."""
        if not vouchers:
            print("No vouchers to display.")
            return
        
        print()
        print("=" * 110)
        print("VOUCHERS WITHOUT COST CENTRE")
        print("=" * 110)
        print()
        print(f"{'#':<4} {'Voucher ID':<12} {'Date':<12} {'Amount':<12} {'Supplier':<25} {'Description':<30}")
        print("-" * 110)
        
        total_amount = 0
        for i, voucher in enumerate(vouchers, 1):
            voucher_id = voucher.get('id')
            voucher_date = voucher.get('voucherDate', '')[:10]
            amount = float(voucher.get('sumNet', 0))
            total_amount += amount
            supplier = voucher.get('supplierNameAtSave', 'N/A')[:24]
            description = voucher.get('description', '')[:29]
            
            print(f"{i:<4} {voucher_id:<12} {voucher_date:<12} €{amount:>9.2f}  {supplier:<25} {description:<30}")
        
        print("-" * 110)
        print(f"{'Total:':<28} €{total_amount:>9.2f}")
        print()
    
    def get_voucher_positions(self, voucher_id: str) -> List[Dict]:
        """Get all positions for a voucher."""
        try:
            # Try the correct API endpoint format
            response = self.client._request('GET', f'/Voucher/{voucher_id}/getPositions')
            if response and 'objects' in response:
                return response['objects']
        except Exception as e:
            # Ignore error and return empty list
            pass
        return []
    
    def update_voucher_cost_centre(self, voucher_id: str) -> bool:
        """
        Update a voucher to assign the Bar-Kollekten cost centre 
        and change accounting type to Spendeneingang.
        
        Args:
            voucher_id: ID of the voucher to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Step 1: Update the voucher with cost centre
            update_data = {
                'id': voucher_id,
                'objectName': 'Voucher',
                'costCentre': {
                    'id': BAR_KOLLEKTEN_COST_CENTRE_ID,
                    'objectName': 'CostCentre'
                }
            }
            
            response = self.client._request(
                'PUT',
                f'/Voucher/{voucher_id}',
                data=update_data
            )
            
            if not response or 'objects' not in response:
                return False
            
            # Step 2: Update voucher positions with new accounting type
            positions = self.get_voucher_positions(voucher_id)
            
            for position in positions:
                position_id = position.get('id')
                if position_id:
                    pos_update_data = {
                        'id': position_id,
                        'objectName': 'VoucherPos',
                        'accountingType': {
                            'id': SPENDENEINGANG_ACCOUNTING_TYPE_ID,
                            'objectName': 'AccountingType'
                        }
                    }
                    
                    try:
                        self.client._request(
                            'PUT',
                            f'/VoucherPos/{position_id}',
                            data=pos_update_data
                        )
                    except Exception as e:
                        # Continue even if position update fails
                        print(f"  ⚠️  Warning: Could not update position {position_id}: {str(e)}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def fix_single_voucher(self, vouchers: List[Dict]) -> int:
        """Fix a single voucher as a test."""
        if not vouchers:
            print("No vouchers to fix.")
            return 0
        
        voucher = vouchers[0]
        voucher_id = voucher.get('id')
        amount = float(voucher.get('sumNet', 0))
        voucher_date = voucher.get('voucherDate', '')[:10]
        
        print()
        print("=" * 70)
        print("FIXING SINGLE VOUCHER (TEST)")
        print("=" * 70)
        print()
        print(f"Voucher ID: {voucher_id}")
        print(f"Date: {voucher_date}")
        print(f"Amount: €{amount:.2f}")
        print(f"Assigning cost centre: {BAR_KOLLEKTEN_COST_CENTRE_NAME} (ID: {BAR_KOLLEKTEN_COST_CENTRE_ID})")
        print(f"Changing accounting type to: {SPENDENEINGANG_ACCOUNTING_TYPE_NAME} (ID: {SPENDENEINGANG_ACCOUNTING_TYPE_ID})")
        print()
        
        success = self.update_voucher_cost_centre(voucher_id)
        
        if success:
            print(f"✓ Successfully updated voucher {voucher_id}")
            print()
            return 1
        else:
            print(f"✗ Failed to update voucher {voucher_id}")
            print()
            return 0
    
    def fix_all_vouchers(self, vouchers: List[Dict]) -> int:
        """Fix all vouchers."""
        if not vouchers:
            print("No vouchers to fix.")
            return 0
        
        print()
        print("=" * 70)
        print(f"FIXING ALL {len(vouchers)} VOUCHERS")
        print("=" * 70)
        print()
        print(f"Assigning cost centre: {BAR_KOLLEKTEN_COST_CENTRE_NAME} (ID: {BAR_KOLLEKTEN_COST_CENTRE_ID})")
        print(f"Changing accounting type to: {SPENDENEINGANG_ACCOUNTING_TYPE_NAME} (ID: {SPENDENEINGANG_ACCOUNTING_TYPE_ID})")
        print()
        
        success_count = 0
        
        for i, voucher in enumerate(vouchers, 1):
            voucher_id = voucher.get('id')
            amount = float(voucher.get('sumNet', 0))
            voucher_date = voucher.get('voucherDate', '')[:10]
            
            print(f"[{i}/{len(vouchers)}] Updating voucher {voucher_id} (€{amount:.2f}, {voucher_date})...", end=' ')
            
            success = self.update_voucher_cost_centre(voucher_id)
            
            if success:
                print("✓")
                success_count += 1
            else:
                print("✗")
        
        print()
        print("=" * 70)
        print(f"COMPLETED: {success_count}/{len(vouchers)} vouchers updated")
        print("=" * 70)
        print()
        
        return success_count
    
    def generate_report(self, vouchers: List[Dict], output_file: str = "reports/bar_kollekten_to_fix.md"):
        """Generate a markdown report of vouchers that need fixing."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write("# Bar-Kollekten Vouchers Without Cost Centre\n\n")
            f.write(f"**Total:** {len(vouchers)} voucher(s) need cost centre assignment\n\n")
            
            if vouchers:
                f.write("## Vouchers to Fix\n\n")
                f.write("These vouchers need to be assigned to the 'Bar-Kollekten' cost centre:\n\n")
                
                table = self.build_markdown_table(vouchers)
                f.write(table)
                
                f.write("\n## Next Steps\n\n")
                f.write("To fix these vouchers:\n\n")
                f.write("```bash\n")
                f.write("# Test with single voucher first:\n")
                f.write("python3 scripts/fix_bar_kollekten_cost_centre.py --fix-single\n\n")
                f.write("# Then fix all vouchers:\n")
                f.write("python3 scripts/fix_bar_kollekten_cost_centre.py --fix-all\n")
                f.write("```\n")
            else:
                f.write("✅ All vouchers have cost centres assigned!\n")
        
        print(f"📄 Report saved to: {output_file}")
    
    def build_markdown_table(self, vouchers: List[Dict]) -> str:
        """Build a markdown table of vouchers."""
        if not vouchers:
            return "No vouchers to fix.\n"
        
        lines = []
        lines.append("| # | Voucher ID | Date | Amount | Supplier | Description |")
        lines.append("|---|------------|------|--------|----------|-------------|")
        
        total_amount = 0
        for i, voucher in enumerate(vouchers, 1):
            voucher_id = voucher.get('id')
            voucher_date = voucher.get('voucherDate', '')[:10]
            amount = float(voucher.get('sumNet', 0))
            total_amount += amount
            supplier = voucher.get('supplierNameAtSave', 'N/A')[:20]
            description = voucher.get('description', '')[:30]
            
            lines.append(f"| {i} | {voucher_id} | {voucher_date} | €{amount:,.2f} | {supplier} | {description} |")
        
        lines.append("")
        lines.append(f"**Total: {len(vouchers)} voucher(s) - €{total_amount:,.2f}**")
        lines.append("")
        
        return "\n".join(lines)
    
    def run(self, fix_mode: str = None):
        """
        Main execution method.
        
        Args:
            fix_mode: None for overview, 'single' for test, 'all' for all vouchers
        """
        print()
        print("=" * 70)
        print("BAR-KOLLEKTEN COST CENTRE FIXER")
        print("=" * 70)
        print()
        
        self.load_environment()
        self.initialize_api_client()
        self.open_database()
        
        # Get vouchers without cost centre
        vouchers = self.get_vouchers_without_cost_centre()
        
        # Print overview
        self.print_vouchers_overview(vouchers)
        
        # Generate report
        self.generate_report(vouchers)
        
        if not vouchers:
            print("✓ No vouchers need fixing!")
            return
        
        # Process based on mode
        if fix_mode == 'single':
            fixed_count = self.fix_single_voucher(vouchers)
            if fixed_count > 0:
                print()
                print("✅ Test successful! You can now run with --fix-all to fix all vouchers.")
        elif fix_mode == 'all':
            fixed_count = self.fix_all_vouchers(vouchers)
            if fixed_count > 0:
                print()
                print("✅ All vouchers updated!")
                print()
                print("🔄 Next step: Run the Bar-Kollekten marking script:")
                print("   python3 scripts/vouchers/create_all_vouchers.py --run-all")
        else:
            # Overview mode
            print()
            print("=" * 70)
            print("OVERVIEW MODE")
            print("=" * 70)
            print()
            print("To fix these vouchers:")
            print("  - Test with single voucher: python3 scripts/fix_bar_kollekten_cost_centre.py --fix-single")
            print("  - Fix all vouchers:         python3 scripts/fix_bar_kollekten_cost_centre.py --fix-all")
            print()
        
        # Close connections
        if self.db:
            self.db.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Fix Bar-Kollekten vouchers by assigning cost centre'
    )
    parser.add_argument(
        '--fix-single',
        action='store_true',
        help='Fix one voucher as a test'
    )
    parser.add_argument(
        '--fix-all',
        action='store_true',
        help='Fix all vouchers without cost centre'
    )
    
    args = parser.parse_args()
    
    fixer = BarKollektenFixer()
    
    if args.fix_single:
        fixer.run(fix_mode='single')
    elif args.fix_all:
        fixer.run(fix_mode='all')
    else:
        fixer.run(fix_mode=None)


if __name__ == '__main__':
    main()
