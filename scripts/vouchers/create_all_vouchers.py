#!/usr/bin/env python3
"""
Master Voucher Creator - Orchestrates all voucher creation scripts.

This script runs all voucher creators, generates a unified markdown report,
and can create vouchers for all types at once.

Usage:
    python3 create_all_vouchers.py                 # Generate unified plan
    python3 create_all_vouchers.py --create-single # Create one voucher per type
    python3 create_all_vouchers.py --create-all    # Create ALL vouchers
    python3 create_all_vouchers.py --run-all       # Create ALL vouchers AND mark Bar-Kollekten as paid
"""
import os
import sys
import argparse
from typing import List, Dict, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import all voucher creators
from scripts.vouchers.create_vouchers_for_gehalt import GehaltVoucherCreator
from scripts.vouchers.create_vouchers_for_ulp import UlpVoucherCreator
from scripts.vouchers.create_vouchers_for_spenden import SpendenVoucherCreator
from scripts.vouchers.create_vouchers_for_krankenkassen import KrankenkassenVoucherCreator
from scripts.vouchers.create_vouchers_for_grace_baptist import GraceBaptistVoucherCreator
from scripts.vouchers.create_vouchers_for_kontaktmission import KontaktmissionVoucherCreator
from scripts.vouchers.create_vouchers_for_ebtc import EBTCVoucherCreator
from scripts.vouchers.create_vouchers_for_jek_freizeit import JEKFreizeitVoucherCreator
from scripts.vouchers.create_vouchers_for_geldtransit import GeldtransitVoucherCreator
from scripts.vouchers.create_vouchers_for_fees import FeesVoucherCreator


class MasterVoucherCreator:
    """
    Master orchestrator for all voucher creation scripts.
    
    Runs all voucher creators, collects results, generates unified report,
    and optionally creates all vouchers at once.
    """
    
    # Define all voucher creators to run
    VOUCHER_CREATORS = [
        ('gehalt', GehaltVoucherCreator, '💰', 'Gehalt (Salaries)'),
        ('ulp', UlpVoucherCreator, '🎓', 'ÜLP (Übungsleiterpauschale)'),
        ('spenden', SpendenVoucherCreator, '💝', 'Spenden (Donations)'),
        ('krankenkassen', KrankenkassenVoucherCreator, '🏥', 'Krankenkassen (Health Insurance)'),
        ('grace_baptist', GraceBaptistVoucherCreator, '⛪', 'Grace Baptist'),
        ('kontaktmission', KontaktmissionVoucherCreator, '🌍', 'Kontaktmission'),
        ('ebtc', EBTCVoucherCreator, '📚', 'EBTC (Donations)'),
        ('jek_freizeit', JEKFreizeitVoucherCreator, '🏕️', 'JEK Freizeit'),
        ('geldtransit', GeldtransitVoucherCreator, '🏦', 'Geldtransit'),
        ('fees', FeesVoucherCreator, '💳', 'Fees'),
    ]
    
    def __init__(self, create_mode: str = None):
        """
        Initialize master creator.
        
        Args:
            create_mode: None (plan only), 'single', or 'all'
        """
        self.create_mode = create_mode
        self.results: List[Dict] = []
        self.bar_kollekten_vouchers: List[Dict] = []
        self.bar_kollekten_count = 0
        self.total_vouchers = 0
        self.total_created = 0
        self.total_failed = 0
        
    def run_all_creators(self) -> List[Dict]:
        """
        Run all voucher creators and collect results.
        
        Returns:
            List of result dictionaries
        """
        print("=" * 80)
        print("🎯 MASTER VOUCHER CREATOR")
        print("=" * 80)
        print()
        print("Running all voucher creators...")
        print()
        
        for key, creator_class, icon, description in self.VOUCHER_CREATORS:
            print(f"\n{'=' * 80}")
            print(f"{icon} Processing: {description}")
            print('=' * 80)
            
            try:
                result = self._run_single_creator(key, creator_class, icon, description)
                self.results.append(result)
                self.total_vouchers += result['voucher_count']
            except Exception as e:
                print(f"\n❌ Error running {description}: {str(e)}")
                self.results.append({
                    'key': key,
                    'icon': icon,
                    'name': description,
                    'error': str(e),
                    'voucher_count': 0,
                    'voucher_plan': []
                })
        
        return self.results
    
    def _run_single_creator(
        self,
        key: str,
        creator_class,
        icon: str,
        description: str
    ) -> Dict:
        """
        Run a single voucher creator and capture results.
        
        Args:
            key: Voucher type key (e.g., 'gehalt')
            creator_class: Creator class to instantiate
            icon: Icon for display
            description: Human-readable description
            
        Returns:
            Result dictionary with voucher plan
        """
        # Create instance
        creator = creator_class()
        
        # Suppress create mode for planning phase
        original_args = argparse.Namespace(create_single=False, create_all=False)
        creator.args = original_args
        
        # Run the setup
        creator.load_environment()
        
        # Skip reload if already done
        if not hasattr(self, '_data_reloaded'):
            creator.reload_data()
            self._data_reloaded = True
        else:
            print("(Skipping data reload - already done)")
            print()
        
        # Initialize API client
        creator.initialize_api_client()
        
        # Open database and get voucher plan
        voucher_plan = []
        with creator.open_database() as db:
            creator.db = db
            
            # Find accounting type
            if not creator.find_accounting_type(db):
                return {
                    'key': key,
                    'icon': icon,
                    'name': description,
                    'error': 'Accounting type not found',
                    'voucher_count': 0,
                    'voucher_plan': []
                }
            
            # Get and filter transactions
            all_transactions = creator.get_open_transactions(db)
            filtered_transactions = creator.filter_transactions(all_transactions)
            
            if not filtered_transactions:
                print(f"No matching transactions found for {description}")
                return {
                    'key': key,
                    'icon': icon,
                    'name': description,
                    'voucher_count': 0,
                    'voucher_plan': [],
                    'accounting_type': creator.accounting_type
                }
            
            print(f"✓ Found {len(filtered_transactions)} matching transactions")
            
            # Generate voucher plan
            voucher_plan = creator.generate_voucher_plan(filtered_transactions)
        
        return {
            'key': key,
            'icon': icon,
            'name': description,
            'voucher_count': len(voucher_plan),
            'voucher_plan': voucher_plan,
            'creator': creator,
            'accounting_type': creator.accounting_type
        }
    
    def get_bar_kollekten_vouchers(self):
        """
        Get Bar-Kollekten vouchers that need to be marked as paid.
        Returns a markdown table section.
        """
        try:
            # Import from scripts/ directory (one level up)
            sys.path.insert(0, os.path.join(project_root, 'scripts'))
            from mark_bar_kollekten_paid import BarKollektenMarker
            
            print("\n" + "=" * 80)
            print("💰 Checking Bar-Kollekten vouchers to mark as paid...")
            print("=" * 80)
            
            marker = BarKollektenMarker()
            marker.load_environment()
            marker.initialize_api_client()
            marker.open_database()
            
            vouchers = marker.get_open_bar_kollekten_vouchers()
            
            if vouchers:
                print(f"✓ Found {len(vouchers)} Bar-Kollekten vouchers to mark as paid")
                # Store count for later reminder
                self.bar_kollekten_count = len(vouchers)
                # Generate the markdown table
                markdown_table = marker.build_markdown_table(vouchers)
                return markdown_table, len(vouchers)
            else:
                print("✓ No Bar-Kollekten vouchers to mark as paid")
                self.bar_kollekten_count = 0
                return None, 0
                
        except Exception as e:
            print(f"❌ Error checking Bar-Kollekten vouchers: {e}")
            self.bar_kollekten_count = 0
            return None, 0
    
    def generate_unified_markdown(self) -> str:
        """
        Generate unified markdown report for all vouchers.
        
        Returns:
            Path to the generated markdown file
        """
        # Output to project root (two levels up from scripts/vouchers/)
        output_file = os.path.join(project_root, "voucher_plan_all.md")
        
        markdown_lines = []
        
        # Header
        markdown_lines.append("# 📋 Unified Voucher Plan - All Types")
        markdown_lines.append("")
        markdown_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        markdown_lines.append(f"**Total Vouchers:** {self.total_vouchers}")
        markdown_lines.append("")
        
        # Summary table
        markdown_lines.append("## 📊 Summary by Type")
        markdown_lines.append("")
        markdown_lines.append("| Icon | Type | Count | Accounting Type | Status |")
        markdown_lines.append("|------|------|-------|-----------------|--------|")
        
        for result in self.results:
            icon = result['icon']
            name = result['name']
            count = result['voucher_count']
            status = "✅ Ready" if count > 0 else "⚪ None"
            
            if 'error' in result:
                status = f"❌ Error"
                accounting_type = "N/A"
            else:
                accounting_type = result.get('accounting_type', {}).get('name', 'N/A')
            
            markdown_lines.append(f"| {icon} | {name} | {count} | {accounting_type} | {status} |")
        
        markdown_lines.append("")
        markdown_lines.append(f"**Total:** {self.total_vouchers} vouchers across {len([r for r in self.results if r['voucher_count'] > 0])} types")
        markdown_lines.append("")
        
        # Detailed sections for each type
        for result in self.results:
            if result['voucher_count'] == 0:
                continue
            
            markdown_lines.append(f"## {result['icon']} {result['name']}")
            markdown_lines.append("")
            markdown_lines.append(f"**Count:** {result['voucher_count']} vouchers")
            markdown_lines.append(f"**Accounting Type:** {result['accounting_type']['name']} (ID: {result['accounting_type']['id']})")
            markdown_lines.append("")
            
            # Determine if this is a donation type (for column selection)
            show_donation = result['key'] == 'spenden'
            
            if show_donation:
                markdown_lines.append("| # | Date | Amount | Donor | Purpose | Type | Cost Centre | Contact |")
                markdown_lines.append("|---|------|--------|-------|---------|------|-------------|---------|")
            else:
                markdown_lines.append("| # | Date | Amount | Payee/Payer | Purpose | Cost Centre | Contact |")
                markdown_lines.append("|---|------|--------|-------------|---------|-------------|---------|")
            
            for i, plan in enumerate(result['voucher_plan'], 1):
                date = plan['transaction_date'][:10]
                amount = plan['amount']
                payee = plan['payee_payer_name'][:30]  # Truncate long names
                purpose = plan.get('payment_purpose', '')[:40]  # Truncate long purposes
                
                cost_centre = plan.get('cost_centre')
                if cost_centre:
                    cc_display = f"✅ {cost_centre['name'][:20]}"
                else:
                    cc_display = "❌"
                
                contact = plan.get('contact')
                contact_display = "✅" if contact else "❌"
                
                if show_donation:
                    donation_type = plan.get('donation_type', 'general')
                    if donation_type == 'mission':
                        type_icon = "🎯"
                    elif donation_type == 'jeske':
                        type_icon = "🔄"
                    elif donation_type == 'tobias':
                        type_icon = "👤"
                    else:
                        type_icon = "💝"
                    
                    markdown_lines.append(
                        f"| {i} | {date} | €{amount:,.2f} | {payee} | {purpose} | "
                        f"{type_icon} {donation_type} | {cc_display} | {contact_display} |"
                    )
                else:
                    markdown_lines.append(
                        f"| {i} | {date} | €{amount:,.2f} | {payee} | {purpose} | "
                        f"{cc_display} | {contact_display} |"
                    )
            
            markdown_lines.append("")
            markdown_lines.append(f"*See individual plan file: `voucher_plan_{result['key']}.md`*")
            markdown_lines.append("")
        
        # Bar-Kollekten section
        bar_kollekten_table, bar_kollekten_count = self.get_bar_kollekten_vouchers()
        if bar_kollekten_table:
            markdown_lines.append("## 💰 Bar-Kollekten - Vouchers to Mark as Paid")
            markdown_lines.append("")
            markdown_lines.append(f"**Count:** {bar_kollekten_count} vouchers")
            markdown_lines.append(f"**Action:** Mark as paid to **Kasse** account")
            markdown_lines.append("")
            markdown_lines.append(bar_kollekten_table)
            markdown_lines.append("")
            markdown_lines.append("**To mark these vouchers as paid:**")
            markdown_lines.append("```bash")
            markdown_lines.append("# Test with single voucher")
            markdown_lines.append("python3 scripts/mark_bar_kollekten_paid.py --mark-single")
            markdown_lines.append("")
            markdown_lines.append("# Mark all vouchers")
            markdown_lines.append("python3 scripts/mark_bar_kollekten_paid.py --mark-all")
            markdown_lines.append("```")
            markdown_lines.append("")
            markdown_lines.append(f"*See detailed report: `reports/bar_kollekten_to_mark.md`*")
            markdown_lines.append("")
        
        # Warnings section
        warnings = []
        for result in self.results:
            if 'error' in result:
                warnings.append(f"- ❌ **{result['name']}**: {result['error']}")
            elif result['voucher_count'] > 0:
                missing_cc = sum(1 for p in result['voucher_plan'] if not p.get('cost_centre'))
                missing_contact = sum(1 for p in result['voucher_plan'] if not p.get('contact'))
                
                if missing_cc > 0:
                    warnings.append(f"- ⚠️  **{result['name']}**: {missing_cc} voucher(s) without cost centre")
                if missing_contact > 0:
                    warnings.append(f"- ⚠️  **{result['name']}**: {missing_contact} voucher(s) without contact")
        
        if warnings:
            markdown_lines.append("## ⚠️ Warnings")
            markdown_lines.append("")
            for warning in warnings:
                markdown_lines.append(warning)
            markdown_lines.append("")
        
        # Next steps
        markdown_lines.append("## 🚀 Next Steps")
        markdown_lines.append("")
        markdown_lines.append("### Option 1: Run Everything at Once")
        markdown_lines.append("```bash")
        markdown_lines.append("# Create ALL vouchers for ALL types AND mark Bar-Kollekten as paid")
        markdown_lines.append("python3 scripts/vouchers/create_all_vouchers.py --run-all")
        markdown_lines.append("```")
        markdown_lines.append("")
        markdown_lines.append("### Option 2: Create Vouchers Only")
        markdown_lines.append("```bash")
        markdown_lines.append("# Test with one voucher per type")
        markdown_lines.append("python3 scripts/vouchers/create_all_vouchers.py --create-single")
        markdown_lines.append("")
        markdown_lines.append("# Create ALL vouchers for ALL types")
        markdown_lines.append("python3 scripts/vouchers/create_all_vouchers.py --create-all")
        markdown_lines.append("```")
        markdown_lines.append("")
        markdown_lines.append("### Option 3: Create by Individual Type")
        markdown_lines.append("```bash")
        
        for result in self.results:
            if result['voucher_count'] > 0:
                script_name = f"create_vouchers_for_{result['key']}.py"
                markdown_lines.append(f"python3 scripts/vouchers/{script_name} --create-all  # {result['icon']} {result['name']}")
        
        markdown_lines.append("```")
        markdown_lines.append("")
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_lines))
        
        return output_file
    
    def print_summary(self, output_file: str):
        """Print console summary of all results."""
        print("\n" + "=" * 80)
        print("📋 UNIFIED VOUCHER PLAN GENERATED")
        print("=" * 80)
        print()
        print(f"✓ Plan saved to: {output_file}")
        print()
        
        # Summary table
        print("Summary by Type:")
        print(f"{'Icon':<6} {'Type':<35} {'Count':<8} {'Status':<10}")
        print("-" * 70)
        
        for result in self.results:
            icon = result['icon']
            name = result['name']
            count = result['voucher_count']
            
            if 'error' in result:
                status = "❌ Error"
            elif count > 0:
                status = "✅ Ready"
            else:
                status = "⚪ None"
            
            print(f"{icon:<6} {name:<35} {count:<8} {status:<10}")
        
        print("-" * 70)
        print(f"{'TOTAL':<42} {self.total_vouchers:<8}")
        print()
        
        # Warnings
        has_warnings = False
        for result in self.results:
            if 'error' in result:
                if not has_warnings:
                    print("⚠️  Warnings:")
                    has_warnings = True
                print(f"   ❌ {result['name']}: {result['error']}")
        
        if has_warnings:
            print()
        
        print("Next steps:")
        print(f"  1. Review the unified plan: {output_file}")
        print("  2. Test with one voucher per type: python3 create_all_vouchers.py --create-single")
        print("  3. Create all vouchers: python3 create_all_vouchers.py --create-all")
        if self.bar_kollekten_count > 0:
            print(f"  4. OR run everything at once: python3 create_all_vouchers.py --run-all")
            print(f"     (creates vouchers + marks {self.bar_kollekten_count} Bar-Kollekten as paid)")
        print()
        print("=" * 80)
    
    def create_all_vouchers(self, create_single: bool = False):
        """
        Create vouchers for all types.
        
        Args:
            create_single: If True, create only one voucher per type (test mode)
        """
        print("\n" + "=" * 80)
        print("🚀 CREATING VOUCHERS FOR ALL TYPES")
        print("=" * 80)
        print()
        
        mode = "single voucher per type (TEST MODE)" if create_single else "ALL vouchers"
        print(f"Mode: {mode}")
        print()
        
        # Filter results with vouchers
        results_with_vouchers = [r for r in self.results if r['voucher_count'] > 0]
        
        if not results_with_vouchers:
            print("❌ No vouchers to create!")
            return
        
        # Show what will be created
        print("Will create vouchers for:")
        total_to_create = 0
        for result in results_with_vouchers:
            count = 1 if create_single else result['voucher_count']
            total_to_create += count
            print(f"  {result['icon']} {result['name']}: {count} voucher(s)")
        print()
        print(f"Total vouchers to create: {total_to_create}")
        print()
        
        # Confirm
        response = input("⚠️  Do you want to proceed? (y/N): ").strip().lower()
        if response != 'y':
            print("\n❌ Cancelled by user.")
            return
        
        print()
        
        # Create vouchers for each type
        for result in results_with_vouchers:
            print(f"\n{'=' * 80}")
            print(f"{result['icon']} Creating vouchers for: {result['name']}")
            print('=' * 80)
            
            creator = result['creator']
            voucher_plan = result['voucher_plan']
            
            # Set create mode
            creator.args = argparse.Namespace(
                create_single=create_single,
                create_all=not create_single
            )
            
            try:
                # Get check account and sev client IDs from first transaction
                import json
                first_txn = voucher_plan[0]
                # We need to get the raw transaction data
                with creator.open_database() as db:
                    creator.db = db
                    all_txns = db.get_all_transactions(status=100)
                    matching_txn = next((t for t in all_txns if t['id'] == first_txn['transaction_id']), None)
                    
                    if matching_txn:
                        raw_data = json.loads(matching_txn.get('raw_data', '{}'))
                        check_account_id = raw_data.get('checkAccount', {}).get('id')
                        sev_client_id = raw_data.get('sevClient', {}).get('id')
                        
                        # Create vouchers
                        created, failed = creator.create_vouchers(
                            voucher_plan,
                            check_account_id,
                            sev_client_id
                        )
                        
                        self.total_created += len(created)
                        self.total_failed += len(failed)
                        
                        creator.print_creation_summary(created, failed)
                        
                        if created:
                            creator.verify_transaction_statuses(created)
                    else:
                        print(f"❌ Could not find transaction data for {result['name']}")
                        self.total_failed += len(voucher_plan)
                        
            except Exception as e:
                print(f"❌ Error creating vouchers for {result['name']}: {str(e)}")
                self.total_failed += len(voucher_plan)
        
        # Final summary
        print("\n" + "=" * 80)
        print("🎉 ALL VOUCHER CREATION COMPLETED")
        print("=" * 80)
        print()
        print(f"✓ Successfully created: {self.total_created} voucher(s)")
        if self.total_failed > 0:
            print(f"❌ Failed: {self.total_failed} voucher(s)")
        print()
        
        # Bar-Kollekten reminder (only show if not in run_all mode)
        if self.bar_kollekten_count > 0:
            print("=" * 80)
            print("⚠️  REMINDER: BAR-KOLLEKTEN VOUCHERS")
            print("=" * 80)
            print()
            print(f"💰 There are {self.bar_kollekten_count} Bar-Kollekten vouchers that need to be marked as paid.")
            print("   These vouchers already exist and just need payment recording.")
            print()
            print("   To mark them as paid:")
            print("     • Standalone:    python3 scripts/mark_bar_kollekten_paid.py --mark-all")
            print("     • Or use:        python3 scripts/vouchers/create_all_vouchers.py --run-all")
            print("                      (creates vouchers + marks Bar-Kollekten)")
            print()
        
        print("=" * 80)
    
    def mark_bar_kollekten_vouchers(self):
        """
        Mark all Bar-Kollekten vouchers as paid.
        
        Returns:
            Tuple of (marked_count, failed_count)
        """
        try:
            # Import from scripts/ directory (one level up)
            sys.path.insert(0, os.path.join(project_root, 'scripts'))
            from mark_bar_kollekten_paid import BarKollektenMarker
            
            print("\n" + "=" * 80)
            print("💰 MARKING BAR-KOLLEKTEN VOUCHERS AS PAID")
            print("=" * 80)
            print()
            
            marker = BarKollektenMarker()
            marker.load_environment()
            marker.initialize_api_client()
            marker.open_database()
            
            vouchers = marker.get_open_bar_kollekten_vouchers()
            
            if not vouchers:
                print("✓ No Bar-Kollekten vouchers to mark")
                return 0, 0
            
            print(f"\n📋 Found {len(vouchers)} vouchers to mark as paid")
            print(f"💳 Payment account: Kasse (ID: 5472950)")
            print()
            
            marked_count = 0
            failed_count = 0
            
            for i, voucher in enumerate(vouchers, 1):
                voucher_id = voucher.get('id')
                voucher_date = voucher.get('voucherDate', '')[:10]
                amount = float(voucher.get('sumNet', 0))
                
                print(f"[{i}/{len(vouchers)}] Marking voucher {voucher_id} (€{amount:,.2f})...", end=' ')
                
                if marker.mark_voucher_as_paid(voucher):
                    marked_count += 1
                    print("✓")
                else:
                    failed_count += 1
                    print("✗")
            
            print()
            print("=" * 80)
            print("💰 BAR-KOLLEKTEN MARKING COMPLETED")
            print("=" * 80)
            print()
            print(f"✓ Successfully marked: {marked_count} voucher(s)")
            if failed_count > 0:
                print(f"❌ Failed: {failed_count} voucher(s)")
            print()
            
            return marked_count, failed_count
            
        except Exception as e:
            print(f"❌ Error marking Bar-Kollekten vouchers: {e}")
            return 0, 0
    
    def run(self, create_single: bool = False, create_all: bool = False, run_all: bool = False):
        """
        Main execution flow.
        
        Args:
            create_single: Create one voucher per type (test mode)
            create_all: Create all vouchers for all types
            run_all: Create all vouchers AND mark Bar-Kollekten as paid
        """
        # Run all creators and collect results
        self.run_all_creators()
        
        # Generate unified markdown
        output_file = self.generate_unified_markdown()
        
        # Print summary
        self.print_summary(output_file)
        
        # Special confirmation for run_all mode (only if there's something to do)
        if run_all and (self.total_vouchers > 0 or self.bar_kollekten_count > 0):
            print("\n" + "=" * 80)
            print("⚠️  RUN-ALL MODE CONFIRMATION")
            print("=" * 80)
            print()
            print("This will:")
            if self.total_vouchers > 0:
                print(f"  1. Create ALL vouchers for ALL types ({self.total_vouchers} voucher(s))")
            if self.bar_kollekten_count > 0:
                action_num = 2 if self.total_vouchers > 0 else 1
                print(f"  {action_num}. Mark {self.bar_kollekten_count} Bar-Kollekten voucher(s) as paid to Kasse")
            print()
            print("⚠️  This is a comprehensive operation that affects multiple vouchers!")
            print()
            response = input("Do you want to proceed with RUN-ALL? (y/N): ").strip().lower()
            if response != 'y':
                print("\n❌ RUN-ALL cancelled by user.")
                return
            print()
        
        # Create vouchers if requested
        if create_single or create_all or run_all:
            self.create_all_vouchers(create_single=create_single)
        
        # Mark Bar-Kollekten vouchers if run_all
        if run_all and self.bar_kollekten_count > 0:
            self.mark_bar_kollekten_vouchers()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Master Voucher Creator - Run all voucher creation scripts'
    )
    parser.add_argument(
        '--create-single',
        action='store_true',
        help='Create one voucher per type (test mode)'
    )
    parser.add_argument(
        '--create-all',
        action='store_true',
        help='Create ALL vouchers for ALL types'
    )
    parser.add_argument(
        '--run-all',
        action='store_true',
        help='Run ALL operations: Create vouchers AND mark Bar-Kollekten as paid'
    )
    args = parser.parse_args()
    
    # Load environment
    load_dotenv()
    
    # Validate
    api_key = os.getenv('SEVDESK_API_KEY')
    if not api_key:
        print("Error: SEVDESK_API_KEY not found in environment variables.")
        sys.exit(1)
    
    # Run master creator
    master = MasterVoucherCreator()
    master.run(
        create_single=args.create_single, 
        create_all=args.create_all,
        run_all=args.run_all
    )


if __name__ == '__main__':
    main()
