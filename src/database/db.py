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
        
        # Create cost centres table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cost_centres (
                id TEXT PRIMARY KEY,
                object_name TEXT,
                create_date TEXT,
                update_date TEXT,
                name TEXT,
                number TEXT,
                color TEXT,
                status INTEGER,
                raw_data TEXT,
                loaded_at TEXT
            )
        ''')
        
        # Create index for cost centre name
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cost_centre_name ON cost_centres(name)
        ''')
        
        # Create accounting types table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounting_types (
                id TEXT PRIMARY KEY,
                object_name TEXT,
                create_date TEXT,
                update_date TEXT,
                name TEXT,
                translationCode TEXT,
                raw_data TEXT,
                loaded_at TEXT
            )
        ''')
        
        # Create index for accounting type name
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_accounting_type_name ON accounting_types(name)
        ''')
        
        # Create categories table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id TEXT PRIMARY KEY,
                object_name TEXT,
                create_date TEXT,
                update_date TEXT,
                name TEXT,
                priority INTEGER,
                code TEXT,
                color TEXT,
                accounting_number TEXT,
                translationCode TEXT,
                raw_data TEXT,
                loaded_at TEXT
            )
        ''')
        
        # Create index for category name
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_category_name ON categories(name)
        ''')
        
        # Create contacts table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                object_name TEXT,
                create_date TEXT,
                update_date TEXT,
                name TEXT,
                customer_number TEXT,
                supplier_number TEXT,
                category_id TEXT,
                category_name TEXT,
                tax_number TEXT,
                vat_number TEXT,
                description TEXT,
                raw_data TEXT,
                loaded_at TEXT
            )
        ''')
        
        # Create indexes for contact searches
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_contact_name ON contacts(name)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_supplier_number ON contacts(supplier_number)
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
    
    def insert_cost_centre(self, cost_centre: Dict) -> bool:
        """
        Insert or update a cost centre in the database.
        
        Args:
            cost_centre: Cost centre dictionary from SevDesk API
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'id': cost_centre.get('id'),
                'object_name': cost_centre.get('objectName'),
                'create_date': cost_centre.get('create'),
                'update_date': cost_centre.get('update'),
                'name': cost_centre.get('name'),
                'number': cost_centre.get('number'),
                'color': cost_centre.get('color'),
                'status': cost_centre.get('status'),
                'raw_data': json.dumps(cost_centre),
                'loaded_at': datetime.now().isoformat()
            }
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO cost_centres (
                    id, object_name, create_date, update_date, name,
                    number, color, status, raw_data, loaded_at
                ) VALUES (
                    :id, :object_name, :create_date, :update_date, :name,
                    :number, :color, :status, :raw_data, :loaded_at
                )
            ''', data)
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting cost centre {cost_centre.get('id')}: {e}")
            return False
    
    def bulk_insert_cost_centres(self, cost_centres: List[Dict]) -> int:
        """
        Insert multiple cost centres in a single transaction.
        
        Args:
            cost_centres: List of cost centre dictionaries
            
        Returns:
            Number of cost centres successfully inserted
        """
        count = 0
        for cost_centre in cost_centres:
            if self.insert_cost_centre(cost_centre):
                count += 1
        return count
    
    def get_all_cost_centres(self) -> List[Dict]:
        """
        Get all cost centres.
        
        Returns:
            List of cost centre dictionaries
        """
        self.cursor.execute('SELECT * FROM cost_centres ORDER BY name')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_cost_centre(self, cost_centre_id: str) -> Optional[Dict]:
        """
        Get a cost centre by ID.
        
        Args:
            cost_centre_id: The cost centre ID
            
        Returns:
            Cost centre dictionary or None if not found
        """
        self.cursor.execute('SELECT * FROM cost_centres WHERE id = ?', (cost_centre_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def insert_accounting_type(self, accounting_type: Dict) -> bool:
        """
        Insert or update an accounting type in the database.
        
        Args:
            accounting_type: Accounting type dictionary from SevDesk API
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'id': accounting_type.get('id'),
                'object_name': accounting_type.get('objectName'),
                'create_date': accounting_type.get('create'),
                'update_date': accounting_type.get('update'),
                'name': accounting_type.get('name'),
                'translationCode': accounting_type.get('translationCode'),
                'raw_data': json.dumps(accounting_type),
                'loaded_at': datetime.now().isoformat()
            }
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO accounting_types (
                    id, object_name, create_date, update_date, name,
                    translationCode, raw_data, loaded_at
                ) VALUES (
                    :id, :object_name, :create_date, :update_date, :name,
                    :translationCode, :raw_data, :loaded_at
                )
            ''', data)
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting accounting type {accounting_type.get('id')}: {e}")
            return False
    
    def bulk_insert_accounting_types(self, accounting_types: List[Dict]) -> int:
        """
        Insert multiple accounting types in a single transaction.
        
        Args:
            accounting_types: List of accounting type dictionaries
            
        Returns:
            Number of accounting types successfully inserted
        """
        count = 0
        for accounting_type in accounting_types:
            if self.insert_accounting_type(accounting_type):
                count += 1
        return count
    
    def get_all_accounting_types(self) -> List[Dict]:
        """
        Get all accounting types ordered by name.
        
        Returns:
            List of accounting type dictionaries
        """
        self.cursor.execute('SELECT * FROM accounting_types ORDER BY name')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_accounting_type(self, accounting_type_id: str) -> Optional[Dict]:
        """
        Get an accounting type by ID.
        
        Args:
            accounting_type_id: The accounting type ID
            
        Returns:
            Accounting type dictionary or None if not found
        """
        self.cursor.execute('SELECT * FROM accounting_types WHERE id = ?', (accounting_type_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def insert_category(self, category: Dict) -> bool:
        """
        Insert or update a category in the database.
        
        Args:
            category: Category dictionary from SevDesk API
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'id': category.get('id'),
                'object_name': category.get('objectName'),
                'create_date': category.get('create'),
                'update_date': category.get('update'),
                'name': category.get('name'),
                'priority': category.get('priority'),
                'code': category.get('code'),
                'color': category.get('color'),
                'accounting_number': category.get('accountingNumber'),
                'translationCode': category.get('translationCode'),
                'raw_data': json.dumps(category),
                'loaded_at': datetime.now().isoformat()
            }
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO categories (
                    id, object_name, create_date, update_date, name,
                    priority, code, color, accounting_number, translationCode,
                    raw_data, loaded_at
                ) VALUES (
                    :id, :object_name, :create_date, :update_date, :name,
                    :priority, :code, :color, :accounting_number, :translationCode,
                    :raw_data, :loaded_at
                )
            ''', data)
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting category {category.get('id')}: {e}")
            return False
    
    def bulk_insert_categories(self, categories: List[Dict]) -> int:
        """
        Insert multiple categories in a single transaction.
        
        Args:
            categories: List of category dictionaries
            
        Returns:
            Number of categories successfully inserted
        """
        count = 0
        for category in categories:
            if self.insert_category(category):
                count += 1
        return count
    
    def get_all_categories(self) -> List[Dict]:
        """
        Get all categories ordered by priority and name.
        
        Returns:
            List of category dictionaries
        """
        self.cursor.execute('SELECT * FROM categories ORDER BY priority, name')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def insert_contact(self, contact: Dict) -> bool:
        """
        Insert or update a contact in the database.
        
        Args:
            contact: Contact dictionary from SevDesk API
            
        Returns:
            True if successful, False otherwise
        """
        try:
            category = contact.get('category', {}) or {}
            
            # Construct name from surename and familyname if name field is not set
            name = contact.get('name')
            if not name:
                surename = (contact.get('surename') or '').strip()
                familyname = (contact.get('familyname') or '').strip()
                if surename or familyname:
                    name = f"{surename} {familyname}".strip()
            
            data = {
                'id': str(contact.get('id')),
                'object_name': contact.get('objectName'),
                'create_date': contact.get('create'),
                'update_date': contact.get('update'),
                'name': name,
                'customer_number': contact.get('customerNumber'),
                'supplier_number': contact.get('supplierNumber'),
                'category_id': category.get('id') if category else None,
                'category_name': category.get('name') if category else None,
                'tax_number': contact.get('taxNumber'),
                'vat_number': contact.get('vatNumber'),
                'description': contact.get('description'),
                'raw_data': json.dumps(contact),
                'loaded_at': datetime.now().isoformat()
            }
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO contacts (
                    id, object_name, create_date, update_date, name,
                    customer_number, supplier_number, category_id, category_name,
                    tax_number, vat_number, description, raw_data, loaded_at
                ) VALUES (
                    :id, :object_name, :create_date, :update_date, :name,
                    :customer_number, :supplier_number, :category_id, :category_name,
                    :tax_number, :vat_number, :description, :raw_data, :loaded_at
                )
            ''', data)
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting contact {contact.get('id')}: {e}")
            return False
    
    def bulk_insert_contacts(self, contacts: List[Dict]) -> int:
        """
        Insert multiple contacts in a single transaction.
        
        Args:
            contacts: List of contact dictionaries
            
        Returns:
            Number of contacts successfully inserted
        """
        count = 0
        for contact in contacts:
            if self.insert_contact(contact):
                count += 1
        return count
    
    def get_all_contacts(self) -> List[Dict]:
        """
        Get all contacts ordered by name.
        
        Returns:
            List of contact dictionaries
        """
        self.cursor.execute('SELECT * FROM contacts ORDER BY name')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_category(self, category_id: str) -> Optional[Dict]:
        """
        Get a category by ID.
        
        Args:
            category_id: The category ID
            
        Returns:
            Category dictionary or None if not found
        """
        self.cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
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
