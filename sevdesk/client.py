"""SevDesk API Client for fetching transactions and other data."""
import requests
import time
from typing import Dict, List, Optional


class SevDeskClient:
    """Client for interacting with the SevDesk API."""
    
    def __init__(self, api_key: str, base_url: str = "https://my.sevdesk.de/api/v1"):
        """
        Initialize the SevDesk API client.
        
        Args:
            api_key: Your SevDesk API key
            base_url: Base URL for the SevDesk API (default: https://my.sevdesk.de/api/v1)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': api_key,
            'Content-Type': 'application/json'
        })
        self.rate_limit_delay = 0.1  # 100ms between requests
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement simple rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                 data: Optional[Dict] = None) -> Dict:
        """
        Make a request to the SevDesk API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., '/CheckAccountTransaction')
            params: Query parameters
            data: Request body data
            
        Returns:
            Response data as dictionary
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        self._rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Response: {response.text if response else 'No response'}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            raise
    
    def get_transactions(self, limit: int = 1000, offset: int = 0, 
                        status: Optional[int] = None) -> List[Dict]:
        """
        Fetch transactions from SevDesk API.
        
        Args:
            limit: Maximum number of transactions to fetch (default: 1000)
            offset: Offset for pagination (default: 0)
            status: Filter by transaction status (100=Open, 200=Linked, 300=Booked)
            
        Returns:
            List of transaction dictionaries
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if status is not None:
            params['status'] = status
        
        response = self._request('GET', '/CheckAccountTransaction', params=params)
        
        if response and 'objects' in response:
            return response['objects']
        return []
    
    def get_all_transactions(self, status: Optional[int] = None) -> List[Dict]:
        """
        Fetch ALL transactions from SevDesk API using pagination.
        
        Args:
            status: Filter by transaction status (100=Open, 200=Linked, 300=Booked)
            
        Returns:
            List of all transaction dictionaries
        """
        all_transactions = []
        limit = 1000
        offset = 0
        
        while True:
            print(f"Fetching transactions {offset} to {offset + limit}...")
            transactions = self.get_transactions(limit=limit, offset=offset, status=status)
            
            if not transactions:
                break
            
            all_transactions.extend(transactions)
            
            # If we got fewer transactions than the limit, we've reached the end
            if len(transactions) < limit:
                break
            
            offset += limit
        
        print(f"Total transactions fetched: {len(all_transactions)}")
        return all_transactions
    
    def get_transaction(self, transaction_id: str) -> Optional[Dict]:
        """
        Fetch a single transaction by ID.
        
        Args:
            transaction_id: The transaction ID
            
        Returns:
            Transaction dictionary or None if not found
        """
        response = self._request('GET', f'/CheckAccountTransaction/{transaction_id}')
        
        if response and 'objects' in response and len(response['objects']) > 0:
            return response['objects'][0]
        return None
    
    def update_transaction(self, transaction_id: str, data: Dict) -> Dict:
        """
        Update a transaction.
        
        Args:
            transaction_id: The transaction ID
            data: Updated transaction data
            
        Returns:
            Updated transaction dictionary
        """
        return self._request('PUT', f'/CheckAccountTransaction/{transaction_id}', data=data)
    
    def test_connection(self) -> bool:
        """
        Test the API connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to fetch one transaction to test the connection
            self.get_transactions(limit=1)
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
