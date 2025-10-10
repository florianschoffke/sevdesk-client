#!/usr/bin/env python3
"""Load contacts (suppliers/customers) from SevDesk API and store them in the database."""
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
    """Main function."""
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('SEVDESK_API_KEY')
    api_url = os.getenv('SEVDESK_API_URL', 'https://my.sevdesk.de/api/v1')
    db_path = os.getenv('DB_PATH', 'transactions.db')
    
    if not api_key:
        print("Error: SEVDESK_API_KEY not found in environment variables.")
        return
    
    print("=" * 60)
    print("SevDesk Contact Loader")
    print("=" * 60)
    print()
    
    # Initialize API client
    print(f"Connecting to SevDesk API at {api_url}...")
    client = SevDeskClient(api_key=api_key, base_url=api_url)
    
    # Test connection
    if not client.test_connection():
        print("✗ Connection failed!")
        return
    
    print("✓ Connection successful!")
    print()
    
    # Fetch contacts
    print("Fetching contacts from SevDesk...")
    contacts = client.get_contacts()
    print(f"✓ Fetched {len(contacts)} contacts")
    print()
    
    # Open database and store contacts
    print(f"Opening database: {db_path}")
    with TransactionDB(db_path=db_path) as db:
        # Get current count
        current_contacts = db.get_all_contacts()
        print(f"Current contacts in database: {len(current_contacts)}")
        print()
        
        # Insert contacts
        print("Inserting contacts into database...")
        count = db.bulk_insert_contacts(contacts)
        print(f"✓ Successfully inserted/updated {count} contacts")
        print()
        
        # Get final count
        all_contacts = db.get_all_contacts()
        print(f"Total contacts in database: {len(all_contacts)}")
        print()
        
        # Show some examples
        print("Contacts:")
        print("-" * 60)
        for contact in all_contacts[:20]:  # Show first 20
            contact_id = contact.get('id')
            name = contact.get('name', 'N/A')
            supplier_number = contact.get('supplier_number', 'N/A')
            print(f"  [{contact_id}] {name} (Supplier#: {supplier_number})")
        
        if len(all_contacts) > 20:
            print(f"  ... and {len(all_contacts) - 20} more")
        
        print()
    
    print("=" * 60)
    print("✓ Contact loading completed successfully!")
    print("=" * 60)
    print()
    print(f"Database file: {db_path}")


if __name__ == '__main__':
    main()
