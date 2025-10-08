"""SQLite database operations for storing SevDesk transactions."""
import sqlite3
import json
from typing import Dict, List, Optional
from datetime import datetime


class TransactionDB:
    """SQLite database handler for SevDesk transactions."""
    
    def __init__(self, db_path: str = "transactions.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file (default: transactions.db)
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()
    
    def _create_tables(self):
        """Create the transactions table if it doesn't exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                object_name TEXT,
                create_date TEXT,
                update_date TEXT,
                sev_client_id TEXT,
                value_date TEXT,
                entry_date TEXT,
                paym_purpose TEXT,
                amount REAL,
                paymt_purpose TEXT,
                status INTEGER,
                status_name TEXT,
                check_account_id TEXT,
                check_account_object_name TEXT,
                source_transaction_id TEXT,
                source_transaction_object_name TEXT,
                target_transaction_id TEXT,
                target_transaction_object_name TEXT,
                raw_data TEXT,
                loaded_at TEXT
            )
        ''')
        
        # Create indexes for common queries
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_status ON transactions(status)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_value_date ON transactions(value_date)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_paymt_purpose ON transactions(paymt_purpose)
        ''')
        
        self.conn.commit()
    
    def insert_transaction(self, transaction: Dict) -> bool:
        """
        Insert or update a transaction in the database.
        
        Args:
            transaction: Transaction dictionary from SevDesk API
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Map status to human-readable name
            status_map = {
                100: 'Open',
                200: 'Linked',
                300: 'Booked'
            }
            
            # Extract nested objects safely
            check_account = transaction.get('checkAccount', {})
            source_transaction = transaction.get('sourceTransaction')
            target_transaction = transaction.get('targetTransaction')
            
            data = {
                'id': transaction.get('id'),
                'object_name': transaction.get('objectName'),
                'create_date': transaction.get('create'),
                'update_date': transaction.get('update'),
                'sev_client_id': transaction.get('sevClient', {}).get('id'),
                'value_date': transaction.get('valueDate'),
                'entry_date': transaction.get('entryDate'),
                'paym_purpose': transaction.get('paymPurpose'),
                'amount': float(transaction.get('amount', 0)),
                'paymt_purpose': transaction.get('paymtPurpose'),
                'status': transaction.get('status'),
                'status_name': status_map.get(transaction.get('status'), 'Unknown'),
                'check_account_id': check_account.get('id') if check_account else None,
                'check_account_object_name': check_account.get('objectName') if check_account else None,
                'source_transaction_id': source_transaction.get('id') if source_transaction else None,
                'source_transaction_object_name': source_transaction.get('objectName') if source_transaction else None,
                'target_transaction_id': target_transaction.get('id') if target_transaction else None,
                'target_transaction_object_name': target_transaction.get('objectName') if target_transaction else None,
                'raw_data': json.dumps(transaction),
                'loaded_at': datetime.now().isoformat()
            }
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO transactions (
                    id, object_name, create_date, update_date, sev_client_id,
                    value_date, entry_date, paym_purpose, amount, paymt_purpose,
                    status, status_name, check_account_id, check_account_object_name,
                    source_transaction_id, source_transaction_object_name,
                    target_transaction_id, target_transaction_object_name,
                    raw_data, loaded_at
                ) VALUES (
                    :id, :object_name, :create_date, :update_date, :sev_client_id,
                    :value_date, :entry_date, :paym_purpose, :amount, :paymt_purpose,
                    :status, :status_name, :check_account_id, :check_account_object_name,
                    :source_transaction_id, :source_transaction_object_name,
                    :target_transaction_id, :target_transaction_object_name,
                    :raw_data, :loaded_at
                )
            ''', data)
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting transaction {transaction.get('id')}: {e}")
            return False
    
    def bulk_insert_transactions(self, transactions: List[Dict]) -> int:
        """
        Insert multiple transactions in a single transaction.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Number of transactions successfully inserted
        """
        count = 0
        for transaction in transactions:
            if self.insert_transaction(transaction):
                count += 1
        return count
    
    def get_transaction(self, transaction_id: str) -> Optional[Dict]:
        """
        Get a transaction by ID.
        
        Args:
            transaction_id: The transaction ID
            
        Returns:
            Transaction dictionary or None if not found
        """
        self.cursor.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_transactions(self, status: Optional[int] = None) -> List[Dict]:
        """
        Get all transactions, optionally filtered by status.
        
        Args:
            status: Filter by transaction status (100=Open, 200=Linked, 300=Booked)
            
        Returns:
            List of transaction dictionaries
        """
        if status is not None:
            self.cursor.execute('SELECT * FROM transactions WHERE status = ?', (status,))
        else:
            self.cursor.execute('SELECT * FROM transactions')
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def search_transactions(self, search_term: str) -> List[Dict]:
        """
        Search transactions by payment purpose.
        
        Args:
            search_term: Search term to match in paymt_purpose field
            
        Returns:
            List of matching transaction dictionaries
        """
        self.cursor.execute(
            'SELECT * FROM transactions WHERE paymt_purpose LIKE ?',
            (f'%{search_term}%',)
        )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the transactions in the database.
        
        Returns:
            Dictionary with statistics
        """
        stats = {}
        
        # Total count
        self.cursor.execute('SELECT COUNT(*) FROM transactions')
        stats['total'] = self.cursor.fetchone()[0]
        
        # Count by status
        self.cursor.execute('''
            SELECT status_name, COUNT(*) as count 
            FROM transactions 
            GROUP BY status_name
        ''')
        stats['by_status'] = {row['status_name']: row['count'] for row in self.cursor.fetchall()}
        
        # Total amount
        self.cursor.execute('SELECT SUM(amount) FROM transactions')
        stats['total_amount'] = self.cursor.fetchone()[0] or 0.0
        
        # Date range
        self.cursor.execute('SELECT MIN(value_date), MAX(value_date) FROM transactions')
        min_date, max_date = self.cursor.fetchone()
        stats['date_range'] = {'min': min_date, 'max': max_date}
        
        return stats
    
    def clear_transactions(self) -> bool:
        """
        Delete all transactions from the database.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cursor.execute('DELETE FROM transactions')
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing transactions: {e}")
            return False
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
