#!/usr/bin/env python3
"""
Update imports in all scripts after restructuring.
"""
import os
import re
from pathlib import Path

# Root directory
root = Path('/Users/gematik/dev/tools/sevdesk-client')

# Import replacements
REPLACEMENTS = {
    # Old import -> New import
    'from voucher_creator_base import': 'from src.vouchers.voucher_creator_base import',
    'from voucher_utils import': 'from src.vouchers.voucher_utils import',
    'from sevdesk.client import': 'from src.sevdesk.client import',
    'from database.db import': 'from src.database.db import',
    'from reload_data import': 'from scripts.loaders.reload_data import',
    
    # Specific creator imports for master script
    'from create_vouchers_for_gehalt import': 'from scripts.vouchers.create_vouchers_for_gehalt import',
    'from create_vouchers_for_ulp import': 'from scripts.vouchers.create_vouchers_for_ulp import',
    'from create_vouchers_for_spenden import': 'from scripts.vouchers.create_vouchers_for_spenden import',
    'from create_vouchers_for_krankenkassen import': 'from scripts.vouchers.create_vouchers_for_krankenkassen import',
    'from create_vouchers_for_grace_baptist import': 'from scripts.vouchers.create_vouchers_for_grace_baptist import',
    'from create_vouchers_for_kontaktmission import': 'from scripts.vouchers.create_vouchers_for_kontaktmission import',
}

def update_file(file_path):
    """Update imports in a single file."""
    print(f"Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply replacements
        for old, new in REPLACEMENTS.items():
            if old in content:
                content = content.replace(old, new)
                print(f"  ✓ Replaced: {old}")
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ Updated: {file_path}")
            return True
        else:
            print(f"  - No changes needed")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Main function."""
    print("=" * 80)
    print("Updating imports after restructuring...")
    print("=" * 80)
    print()
    
    updated_count = 0
    
    # Update voucher scripts
    voucher_scripts_dir = root / 'scripts' / 'vouchers'
    for file_path in voucher_scripts_dir.glob('*.py'):
        if update_file(file_path):
            updated_count += 1
    
    # Update loader scripts
    loader_scripts_dir = root / 'scripts' / 'loaders'
    for file_path in loader_scripts_dir.glob('*.py'):
        if update_file(file_path):
            updated_count += 1
    
    print()
    print("=" * 80)
    print(f"✓ Updated {updated_count} files")
    print("=" * 80)

if __name__ == '__main__':
    main()
