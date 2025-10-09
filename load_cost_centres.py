#!/usr/bin/env python3
"""
Load SevDesk cost centres into a SQLite database.

This script fetches cost centres from the SevDesk API and stores them
in a local SQLite database for easy querying and analysis.
"""
import os
import sys
from dotenv import load_dotenv
from sevdesk.client import SevDeskClient
from database.db import TransactionDB


def main():
    """Main function to load cost centres."""
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
    print("SevDesk Cost Centre Loader")
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
    
    # Fetch cost centres
    print("Fetching cost centres from SevDesk...")
    try:
        cost_centres = client.get_cost_centres()
        print(f"✓ Fetched {len(cost_centres)} cost centres")
        print()
    except Exception as e:
        print(f"Error fetching cost centres: {e}")
        sys.exit(1)
    
    # Initialize database
    print(f"Opening database: {db_path}")
    with TransactionDB(db_path=db_path) as db:
        # Get current cost centres count
        before_count = len(db.get_all_cost_centres())
        print(f"Current cost centres in database: {before_count}")
        print()
        
        # Insert cost centres
        print("Inserting cost centres into database...")
        inserted = db.bulk_insert_cost_centres(cost_centres)
        print(f"✓ Successfully inserted/updated {inserted} cost centres")
        print()
        
        # Display cost centres
        all_cost_centres = db.get_all_cost_centres()
        print(f"Total cost centres in database: {len(all_cost_centres)}")
        print()
        
        if all_cost_centres:
            print("Cost Centres:")
            print("-" * 60)
            for cc in all_cost_centres:
                status_str = "Active" if cc['status'] == 100 else "Inactive"
                print(f"  [{cc['number']}] {cc['name']} ({status_str})")
        print()
    
    print("=" * 60)
    print("✓ Cost centre loading completed successfully!")
    print("=" * 60)
    print()
    print(f"Database file: {db_path}")


if __name__ == '__main__':
    main()
