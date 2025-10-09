#!/usr/bin/env python3
"""
Load SevDesk categories into a SQLite database.

This script fetches categories (used to classify voucher positions like 
'Ehrenamtspauschale', 'Büromaterial', etc.) from the SevDesk API 
and stores them in a local SQLite database for easy querying and analysis.
"""
import os
import sys
from dotenv import load_dotenv
from sevdesk.client import SevDeskClient
from database.db import TransactionDB


def main():
    """Main function to load categories."""
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
    print("SevDesk Category Loader")
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
    
    # Fetch categories
    print("Fetching categories from SevDesk...")
    try:
        categories = client.get_categories()
        print(f"✓ Fetched {len(categories)} categories")
        print()
    except Exception as e:
        print(f"Error fetching categories: {e}")
        sys.exit(1)
    
    # Initialize database
    print(f"Opening database: {db_path}")
    with TransactionDB(db_path=db_path) as db:
        # Get current categories count
        before_count = len(db.get_all_categories())
        print(f"Current categories in database: {before_count}")
        print()
        
        # Insert categories
        print("Inserting categories into database...")
        inserted = db.bulk_insert_categories(categories)
        print(f"✓ Successfully inserted/updated {inserted} categories")
        print()
        
        # Display categories grouped by priority
        all_categories = db.get_all_categories()
        print(f"Total categories in database: {len(all_categories)}")
        print()
        
        if all_categories:
            print("Categories (sorted by priority):")
            print("-" * 80)
            current_priority = None
            for cat in all_categories:
                priority = cat.get('priority', 0)
                if priority != current_priority:
                    current_priority = priority
                    if priority:
                        print(f"\n  Priority {priority}:")
                    else:
                        print(f"\n  No Priority:")
                
                code = cat.get('code', 'N/A')
                accounting_num = cat.get('accounting_number', 'N/A')
                name = cat.get('name', 'Unnamed')
                print(f"    [{cat['id']}] {name} (Code: {code}, Acc#: {accounting_num})")
        print()
    
    print("=" * 60)
    print("✓ Category loading completed successfully!")
    print("=" * 60)
    print()
    print(f"Database file: {db_path}")
    print("\nCategories classify what you're booking (e.g., Ehrenamtspauschale, Büromaterial).")
    print("This is different from AccountingTypes which define HOW it's booked.")


if __name__ == '__main__':
    main()
