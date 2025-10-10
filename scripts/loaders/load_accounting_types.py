#!/usr/bin/env python3
"""
Load SevDesk accounting types into a SQLite database.

This script fetches accounting types (used for voucher positions) from the SevDesk API 
and stores them in a local SQLite database for easy querying and analysis.

Accounting types define how a voucher position is booked (e.g., bank booking, creditor, etc.)
"""
import os
import sys
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.sevdesk.client import SevDeskClient
from src.database.db import TransactionDB


def main():
    """Main function to load accounting types."""
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('SEVDESK_API_KEY')
    api_url = os.getenv('SEVDESK_API_URL', 'https://my.sevdesk.de/api/v1')
    db_path = os.getenv('DB_PATH', 'transactions.db')
    
    # Validate API key
    if not api_key:
        print("Error: SEVDESK_API_KEY not found in environment variables.")
        print("Please create a .env file with your API key (see .env.example)")
        sys.exit(1)
    
    print("=" * 60)
    print("SevDesk Accounting Type Loader")
    print("=" * 60)
    print()
    
    # Initialize API client
    print(f"Connecting to SevDesk API at {api_url}...")
    client = SevDeskClient(api_key=api_key, base_url=api_url)
    
    # Test connection
    if not client.test_connection():
        print("Error: Failed to connect to SevDesk API. Please check your API key.")
        sys.exit(1)
    
    print("✓ Connection successful!")
    print()
    
    # Fetch accounting types
    print("Fetching accounting types from SevDesk...")
    try:
        accounting_types = client.get_accounting_types()
        print(f"✓ Fetched {len(accounting_types)} accounting types")
        print()
    except Exception as e:
        print(f"Error fetching accounting types: {e}")
        sys.exit(1)
    
    # Initialize database
    print(f"Opening database: {db_path}")
    with TransactionDB(db_path=db_path) as db:
        # Get current accounting types count
        before_count = len(db.get_all_accounting_types())
        print(f"Current accounting types in database: {before_count}")
        print()
        
        # Insert accounting types
        print("Inserting accounting types into database...")
        inserted = db.bulk_insert_accounting_types(accounting_types)
        print(f"✓ Successfully inserted/updated {inserted} accounting types")
        print()
        
        # Display accounting types
        all_types = db.get_all_accounting_types()
        print(f"Total accounting types in database: {len(all_types)}")
        print()
        
        if all_types:
            print("Accounting Types:")
            print("-" * 80)
            for at in all_types:
                translation = at.get('translationCode', 'N/A')
                name = at.get('name', 'Unnamed')
                print(f"  [{at['id']}] {name} (Translation: {translation})")
        print()
    
    print("=" * 60)
    print("✓ Accounting type loading completed successfully!")
    print("=" * 60)
    print()
    print(f"Database file: {db_path}")
    print("\nAccounting types are used when creating voucher positions.")
    print("Common types: Bank booking (16), Creditor (9), Debitor (8), etc.")


if __name__ == '__main__':
    main()
