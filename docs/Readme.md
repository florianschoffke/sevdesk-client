# SevDesk Transaction Manager

A Python-based tool to manage SevDesk transactions and automate voucher creation using SQLite database.

## Features

### Transaction Management
- Fetch open transactions from SevDesk API
- Store transactions in SQLite database
- Search and filter transactions
- Bulk edit transactions

### Voucher Creation (NEW!)
- **Automated voucher creation** for different transaction types
- **Master orchestrator** to run all voucher types at once
- **6 specialized voucher creators**:
  - 💰 Gehalt (Salaries)
  - 🎓 ÜLP (Übungsleiterpauschale)
  - 💝 Spenden (Donations)
  - 🏥 Krankenkassen (Health Insurance)
  - ⛪ Grace Baptist Donations
  - 🌍 Kontaktmission Donations
- **Unified markdown reports** with summary tables
- **Batch processing** for time savings

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
├── sevdesk/                      # SevDesk API client module
│   ├── __init__.py
│   └── client.py
├── database/                     # Database operations
│   ├── __init__.py
│   └── db.py
├── voucher_creator_base.py       # Base class for voucher creators (NEW!)
├── create_all_vouchers.py        # Master orchestrator for all vouchers (NEW!)
├── create_vouchers_for_*.py      # Individual voucher creators (NEW!)
├── voucher_utils.py              # Shared voucher utilities (NEW!)
├── load_transactions.py          # Load transactions from API
├── reload_data.py                # Reload all data from API
├── requirements.txt              # Python dependencies
├── .env.example                  # Example environment variables
├── REFACTORING_SUMMARY.md        # Refactoring documentation (NEW!)
├── MASTER_VOUCHER_CREATOR_DOCS.md # Master script docs (NEW!)
└── README.md                     # This file
```

## Usage

### Load Transactions
```bash
python3 load_transactions.py
```

This will fetch all open transactions from SevDesk and store them in `transactions.db`.

### Create Vouchers - Master Script (Recommended!)

**Generate unified plan for all voucher types:**
```bash
python3 create_all_vouchers.py
```

**Test mode (create one voucher per type):**
```bash
python3 create_all_vouchers.py --create-single
```

**Create ALL vouchers for ALL types:**
```bash
python3 create_all_vouchers.py --create-all
```

**Output:** `voucher_plan_all.md` - Unified report with:
- Summary table by voucher type
- Detailed voucher lists per type
- Statistics and warnings

### Create Vouchers - Individual Scripts

For focused work on a specific voucher type:

```bash
# Gehalt (Salaries)
python3 create_vouchers_for_gehalt.py
python3 create_vouchers_for_gehalt.py --create-single
python3 create_vouchers_for_gehalt.py --create-all

# ÜLP (Übungsleiterpauschale)
python3 create_vouchers_for_ulp.py --create-all

# Spenden (Donations)
python3 create_vouchers_for_spenden.py --create-all

# Krankenkassen (Health Insurance)
python3 create_vouchers_for_krankenkassen.py --create-all

# Grace Baptist
python3 create_vouchers_for_grace_baptist.py --create-all

# Kontaktmission
python3 create_vouchers_for_kontaktmission.py --create-all
```

## Workflow Example

**Monthly Voucher Processing:**
```bash
# 1. Generate unified overview
python3 create_all_vouchers.py

# 2. Review the plan
open voucher_plan_all.md

# 3. Test with one voucher per type
python3 create_all_vouchers.py --create-single

# 4. Create all vouchers
python3 create_all_vouchers.py --create-all
```

## Documentation

- **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - Code refactoring details and metrics
- **[MASTER_VOUCHER_CREATOR_DOCS.md](MASTER_VOUCHER_CREATOR_DOCS.md)** - Complete master script documentation
- **[REFACTORING_NOTES.md](REFACTORING_NOTES.md)** - Technical refactoring notes

## Architecture

### Voucher Creation System

Built using the **Template Method Pattern** for maximum code reuse:

```python
VoucherCreatorBase (Abstract Base Class)
├── Template methods (common logic)
├── Abstract methods (must implement)
└── Optional override methods

GehaltVoucherCreator(VoucherCreatorBase)
├── Implements: filter_transactions()
├── Implements: build_voucher_plan_item()
└── Inherits: all common functionality

MasterVoucherCreator
├── Orchestrates all voucher creators
├── Generates unified reports
└── Batch creation capabilities
```

### Benefits

- ✅ **38% less code** (928 lines eliminated)
- ✅ **No duplication** - common logic in base class
- ✅ **Easy maintenance** - changes in one place
- ✅ **Fast extensions** - new voucher types in ~100 lines
- ✅ **Consistent behavior** - all scripts follow same flow
- ✅ **Time savings** - master script processes all types at once
