#!/usr/bin/env python3
"""
Convenience wrapper for the master voucher creator.

This script is a simple wrapper that calls the actual implementation
in scripts/vouchers/create_all_vouchers.py, allowing you to run it
from the project root directory.

Usage:
    python3 create_all_vouchers.py                 # Generate unified plan
    python3 create_all_vouchers.py --create-single # Create one voucher per type
    python3 create_all_vouchers.py --create-all    # Create ALL vouchers
"""
import sys
import subprocess
from pathlib import Path

def main():
    # Get the path to the actual script
    script_dir = Path(__file__).parent
    actual_script = script_dir / "scripts" / "vouchers" / "create_all_vouchers.py"
    
    if not actual_script.exists():
        print(f"Error: Could not find {actual_script}")
        sys.exit(1)
    
    # Run the actual script with all arguments passed through
    cmd = [sys.executable, str(actual_script)] + sys.argv[1:]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
