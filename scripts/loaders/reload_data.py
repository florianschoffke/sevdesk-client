#!/usr/bin/env python3
"""
Reload all data from SevDesk API.

This script clears the local database and reloads:
- Transactions
- Cost centres
- Accounting types
- Categories
- Contacts

Use this before running voucher creation scripts to ensure you have the latest data.
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


def reload_all_data(db_path: str = 'transactions.db', api_key: str = None, api_url: str = None):
    """
    Reload all data from the SevDesk API.
    
    Args:
        db_path: Path to the database file
        api_key: SevDesk API key (if None, loads from environment)
        api_url: SevDesk API URL (if None, loads from environment)
    """
    # Load environment variables if not provided
    if not api_key or not api_url:
        load_dotenv()
        api_key = api_key or os.getenv('SEVDESK_API_KEY')
        api_url = api_url or os.getenv('SEVDESK_API_URL', 'https://my.sevdesk.de/api/v1')
    
    if not api_key:
        print("Error: SEVDESK_API_KEY not found in environment variables.")
        return False
    
    print("=" * 80)
    print("SevDesk Data Reload")
    print("=" * 80)
    print()
    
    # Initialize API client
    print(f"Connecting to SevDesk API at {api_url}...")
    client = SevDeskClient(api_key=api_key, base_url=api_url)
    
    # Test connection
    if not client.test_connection():
        print("✗ Connection failed!")
        return False
    
    print("✓ Connection successful!")
    print()
    
    # Open database
    print(f"Opening database: {db_path}")
    with TransactionDB(db_path=db_path) as db:
        # 1. Load Transactions
        print()
        print("-" * 80)
        print("1. Loading Transactions")
        print("-" * 80)
        
        print("Fetching transactions from API...")
        transactions = client.get_all_transactions()
        print(f"✓ Fetched {len(transactions)} transactions")
        
        print("Clearing existing transactions...")
        db.cursor.execute('DELETE FROM transactions')
        db.conn.commit()
        print("✓ Cleared")
        
        print("Inserting transactions...")
        count = db.bulk_insert_transactions(transactions)
        print(f"✓ Inserted {count} transactions")
        
        # 2. Load Cost Centres
        print()
        print("-" * 80)
        print("2. Loading Cost Centres")
        print("-" * 80)
        
        print("Fetching cost centres from API...")
        cost_centres = client.get_cost_centres()
        print(f"✓ Fetched {len(cost_centres)} cost centres")
        
        print("Clearing existing cost centres...")
        db.cursor.execute('DELETE FROM cost_centres')
        db.conn.commit()
        print("✓ Cleared")
        
        print("Inserting cost centres...")
        count = db.bulk_insert_cost_centres(cost_centres)
        print(f"✓ Inserted {count} cost centres")
        
        # 3. Load Accounting Types
        print()
        print("-" * 80)
        print("3. Loading Accounting Types")
        print("-" * 80)
        
        print("Fetching accounting types from API...")
        accounting_types = client.get_accounting_types()
        print(f"✓ Fetched {len(accounting_types)} accounting types")
        
        print("Clearing existing accounting types...")
        db.cursor.execute('DELETE FROM accounting_types')
        db.conn.commit()
        print("✓ Cleared")
        
        print("Inserting accounting types...")
        count = db.bulk_insert_accounting_types(accounting_types)
        print(f"✓ Inserted {count} accounting types")
        
        # 4. Load Categories
        print()
        print("-" * 80)
        print("4. Loading Categories")
        print("-" * 80)
        
        print("Fetching categories from API...")
        categories = client.get_categories()
        print(f"✓ Fetched {len(categories)} categories")
        
        print("Clearing existing categories...")
        db.cursor.execute('DELETE FROM categories')
        db.conn.commit()
        print("✓ Cleared")
        
        print("Inserting categories...")
        count = db.bulk_insert_categories(categories)
        print(f"✓ Inserted {count} categories")
        
        # 5. Load Contacts
        print()
        print("-" * 80)
        print("5. Loading Contacts")
        print("-" * 80)
        
        print("Fetching contacts from API...")
        contacts = client.get_contacts()
        print(f"✓ Fetched {len(contacts)} contacts")
        
        print("Clearing existing contacts...")
        db.cursor.execute('DELETE FROM contacts')
        db.conn.commit()
        print("✓ Cleared")
        
        print("Inserting contacts...")
        count = db.bulk_insert_contacts(contacts)
        print(f"✓ Inserted {count} contacts")
    
    print()
    print("=" * 80)
    print("✓ Data reload completed successfully!")
    print("=" * 80)
    print()
    
    return True


def main():
    """Main function."""
    load_dotenv()
    
    api_key = os.getenv('SEVDESK_API_KEY')
    api_url = os.getenv('SEVDESK_API_URL', 'https://my.sevdesk.de/api/v1')
    db_path = os.getenv('DB_PATH', 'transactions.db')
    
    success = reload_all_data(db_path=db_path, api_key=api_key, api_url=api_url)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
