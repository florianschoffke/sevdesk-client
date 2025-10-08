# SevDesk Transaction Manager

A Python-based tool to manage SevDesk transactions using SQLite database.

## Features

- Fetch open transactions from SevDesk API
- Store transactions in SQLite database
- Search and filter transactions
- Bulk edit transactions

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with your SevDesk API credentials:
```bash
cp .env.example .env
# Edit .env and add your API key
```

3. Run the transaction loader:
```bash
python load_transactions.py
```

## Project Structure

```
.
├── sevdesk/              # SevDesk API client module
│   ├── __init__.py
│   └── client.py
├── database/             # Database operations
│   ├── __init__.py
│   └── db.py
├── load_transactions.py  # Main script to load transactions
├── requirements.txt      # Python dependencies
├── .env.example         # Example environment variables
└── README.md            # This file
```

## Usage

### Load Transactions
```bash
python load_transactions.py
```

This will fetch all open transactions from SevDesk and store them in `transactions.db`.
