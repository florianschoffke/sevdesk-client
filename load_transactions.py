#!/usr/bin/env python3
"""
Load SevDesk transactions into a SQLite database.

This script fetches open transactions from the SevDesk API and stores them
in a local SQLite database for easy querying and analysis.
"""
import os
import sys
from dotenv import load_dotenv
from sevdesk.client import SevDeskClient
from database.db import TransactionDB


def main():
    """Main function to load transactions."""
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
    print("SevDesk Transaction Loader")
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
    
    # Fetch open transactions (status=100)
    print("Fetching open transactions from SevDesk...")
    try:
        transactions = client.get_all_transactions(status=100)
        print(f"✓ Fetched {len(transactions)} open transactions")
        print()
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        sys.exit(1)
    
    # Initialize database
    print(f"Opening database: {db_path}")
    with TransactionDB(db_path=db_path) as db:
        # Get current statistics
        before_stats = db.get_statistics()
        print(f"Current database stats:")
        print(f"  - Total transactions: {before_stats['total']}")
        print(f"  - By status: {before_stats['by_status']}")
        print()
        
        # Insert transactions
        print("Inserting transactions into database...")
        inserted = db.bulk_insert_transactions(transactions)
        print(f"✓ Successfully inserted/updated {inserted} transactions")
        print()
        
        # Get updated statistics
        after_stats = db.get_statistics()
        print("Updated database stats:")
        print(f"  - Total transactions: {after_stats['total']}")
        print(f"  - By status: {after_stats['by_status']}")
        print(f"  - Total amount: €{after_stats['total_amount']:,.2f}")
        print(f"  - Date range: {after_stats['date_range']['min']} to {after_stats['date_range']['max']}")
        print()
    
    print("=" * 60)
    print("✓ Transaction loading completed successfully!")
    print("=" * 60)
    print()
    print(f"Database file: {db_path}")
    print("You can now query the database using Python or any SQLite client.")


if __name__ == '__main__':
    main()
