# SevDesk Transaction Manager# SevDesk Transaction Manager



A Python-based tool to manage SevDesk transactions and automate voucher creation using SQLite database.A Python-based tool to manage SevDesk transactions and automate voucher creation using SQLite database.



## Features## Features



### Transaction Management### Transaction Management

- Fetch open transactions from SevDesk API- Fetch open transactions from SevDesk API

- Store transactions in SQLite database- Store transactions in SQLite database

- Search and filter transactions- Search and filter transactions

- Bulk edit transactions- Bulk edit transactions



### Voucher Creation### Voucher Creation (NEW!)

- **Automated voucher creation** for different transaction types- **Automated voucher creation** for different transaction types

- **Master orchestrator** to run all voucher types at once- **Master orchestrator** to run all voucher types at once

- **6 specialized voucher creators**:- **6 specialized voucher creators**:

  - 💰 Gehalt (Salaries)  - 💰 Gehalt (Salaries)

  - 🎓 ÜLP (Übungsleiterpauschale)  - 🎓 ÜLP (Übungsleiterpauschale)

  - 💝 Spenden (Donations)  - 💝 Spenden (Donations)

  - 🏥 Krankenkassen (Health Insurance)  - 🏥 Krankenkassen (Health Insurance)

  - ⛪ Grace Baptist Donations  - ⛪ Grace Baptist Donations

  - 🌍 Kontaktmission Donations  - 🌍 Kontaktmission Donations

- **Unified markdown reports** with summary tables- **Unified markdown reports** with summary tables

- **Batch processing** for time savings- **Batch processing** for time savings



## Setup## Setup



1. Install dependencies:1. Install dependencies:

```bash```bash

pip install -r requirements.txtpip install -r requirements.txt

``````



2. Create `.env` file with your SevDesk API credentials:2. Create `.env` file with your SevDesk API credentials:

```bash```bash

cp .env.example .envcp .env.example .env

# Edit .env and add your API key# Edit .env and add your API key

``````



3. Reload data from SevDesk:3. Run the transaction loader:

```bash```bash

python3 scripts/loaders/reload_data.pypython load_transactions.py

``````



## Project Structure## Project Structure



``````

..

├── src/                          # Core library code├── sevdesk/                      # SevDesk API client module

│   ├── sevdesk/                  # SevDesk API client│   ├── __init__.py

│   │   ├── __init__.py│   └── client.py

│   │   └── client.py├── database/                     # Database operations

│   ├── database/                 # Database operations│   ├── __init__.py

│   │   ├── __init__.py│   └── db.py

│   │   └── db.py├── voucher_creator_base.py       # Base class for voucher creators (NEW!)

│   └── vouchers/                 # Voucher creation framework├── create_all_vouchers.py        # Master orchestrator for all vouchers (NEW!)

│       ├── __init__.py├── create_vouchers_for_*.py      # Individual voucher creators (NEW!)

│       ├── voucher_creator_base.py   # Base class (Template Method Pattern)├── voucher_utils.py              # Shared voucher utilities (NEW!)

│       └── voucher_utils.py          # Shared utilities├── load_transactions.py          # Load transactions from API

├── scripts/                      # Executable scripts├── reload_data.py                # Reload all data from API

│   ├── loaders/                  # Data loading scripts├── requirements.txt              # Python dependencies

│   │   ├── load_transactions.py├── .env.example                  # Example environment variables

│   │   ├── load_contacts.py├── REFACTORING_SUMMARY.md        # Refactoring documentation (NEW!)

│   │   ├── load_categories.py├── MASTER_VOUCHER_CREATOR_DOCS.md # Master script docs (NEW!)

│   │   ├── load_cost_centres.py└── README.md                     # This file

│   │   ├── load_accounting_types.py```

│   │   └── reload_data.py        # Reload all data

│   └── vouchers/                 # Voucher creation scripts## Usage

│       ├── create_all_vouchers.py    # Master orchestrator

│       ├── create_vouchers_for_gehalt.py### Load Transactions

│       ├── create_vouchers_for_ulp.py```bash

│       ├── create_vouchers_for_spenden.pypython3 load_transactions.py

│       ├── create_vouchers_for_krankenkassen.py```

│       ├── create_vouchers_for_grace_baptist.py

│       └── create_vouchers_for_kontaktmission.pyThis will fetch all open transactions from SevDesk and store them in `transactions.db`.

├── docs/                         # Documentation

│   ├── REFACTORING_SUMMARY.md### Create Vouchers - Master Script (Recommended!)

│   ├── MASTER_VOUCHER_CREATOR_DOCS.md

│   ├── MASTER_SCRIPT_COMPLETE.md**Generate unified plan for all voucher types:**

│   └── Readme.md```bash

├── reports/                      # Generated voucher planspython3 create_all_vouchers.py

│   ├── voucher_plan_all.md       # Unified report```

│   └── voucher_plan_*.md         # Individual reports

├── backup/                       # Backups**Test mode (create one voucher per type):**

├── tests/                        # Unit tests (future)```bash

├── requirements.txt              # Python dependenciespython3 create_all_vouchers.py --create-single

├── .env.example                  # Example environment variables```

├── transactions.db               # SQLite database

└── README.md                     # This file**Create ALL vouchers for ALL types:**

``````bash

python3 create_all_vouchers.py --create-all

## Usage```



### Load Data**Output:** `voucher_plan_all.md` - Unified report with:

- Summary table by voucher type

**Reload all data from SevDesk:**- Detailed voucher lists per type

```bash- Statistics and warnings

python3 scripts/loaders/reload_data.py

```### Create Vouchers - Individual Scripts



This reloads:For focused work on a specific voucher type:

- Transactions

- Cost centres```bash

- Accounting types# Gehalt (Salaries)

- Categoriespython3 create_vouchers_for_gehalt.py

- Contactspython3 create_vouchers_for_gehalt.py --create-single

python3 create_vouchers_for_gehalt.py --create-all

**Load specific data types:**

```bash# ÜLP (Übungsleiterpauschale)

python3 scripts/loaders/load_transactions.pypython3 create_vouchers_for_ulp.py --create-all

python3 scripts/loaders/load_contacts.py

python3 scripts/loaders/load_categories.py# Spenden (Donations)

python3 scripts/loaders/load_cost_centres.pypython3 create_vouchers_for_spenden.py --create-all

python3 scripts/loaders/load_accounting_types.py

```# Krankenkassen (Health Insurance)

python3 create_vouchers_for_krankenkassen.py --create-all

### Create Vouchers - Master Script (Recommended!)

# Grace Baptist

**Generate unified plan for all voucher types:**python3 create_vouchers_for_grace_baptist.py --create-all

```bash

python3 scripts/vouchers/create_all_vouchers.py# Kontaktmission

```python3 create_vouchers_for_kontaktmission.py --create-all

```

**Test mode (create one voucher per type):**

```bash## Workflow Example

python3 scripts/vouchers/create_all_vouchers.py --create-single

```**Monthly Voucher Processing:**

```bash

**Create ALL vouchers for ALL types:**# 1. Generate unified overview

```bashpython3 create_all_vouchers.py

python3 scripts/vouchers/create_all_vouchers.py --create-all

```# 2. Review the plan

open voucher_plan_all.md

**Output:** `voucher_plan_all.md` - Unified report with:

- Summary table by voucher type# 3. Test with one voucher per type

- Detailed voucher lists per typepython3 create_all_vouchers.py --create-single

- Statistics and warnings

# 4. Create all vouchers

### Create Vouchers - Individual Scriptspython3 create_all_vouchers.py --create-all

```

For focused work on a specific voucher type:

## Documentation

**Generate plan for specific type:**

```bash- **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - Code refactoring details and metrics

python3 scripts/vouchers/create_vouchers_for_spenden.py- **[MASTER_VOUCHER_CREATOR_DOCS.md](MASTER_VOUCHER_CREATOR_DOCS.md)** - Complete master script documentation

```- **[REFACTORING_NOTES.md](REFACTORING_NOTES.md)** - Technical refactoring notes



**Create single voucher (test mode):**## Architecture

```bash

python3 scripts/vouchers/create_vouchers_for_spenden.py --create-single### Voucher Creation System

```

Built using the **Template Method Pattern** for maximum code reuse:

**Create all vouchers for this type:**

```bash```python

python3 scripts/vouchers/create_vouchers_for_spenden.py --create-allVoucherCreatorBase (Abstract Base Class)

```├── Template methods (common logic)

├── Abstract methods (must implement)

Available scripts:└── Optional override methods

- `create_vouchers_for_gehalt.py` - Salaries

- `create_vouchers_for_ulp.py` - ÜbungsleiterpauschaleGehaltVoucherCreator(VoucherCreatorBase)

- `create_vouchers_for_spenden.py` - Donations├── Implements: filter_transactions()

- `create_vouchers_for_krankenkassen.py` - Health Insurance├── Implements: build_voucher_plan_item()

- `create_vouchers_for_grace_baptist.py` - Grace Baptist donations└── Inherits: all common functionality

- `create_vouchers_for_kontaktmission.py` - Kontaktmission donations

MasterVoucherCreator

## Architecture├── Orchestrates all voucher creators

├── Generates unified reports

### Voucher Creator Framework└── Batch creation capabilities

```

The project uses the **Template Method Pattern** to eliminate code duplication:

### Benefits

```python

VoucherCreatorBase (abstract)- ✅ **38% less code** (928 lines eliminated)

├── run()                          # Template method- ✅ **No duplication** - common logic in base class

├── filter_transactions()          # Abstract - implement in subclass- ✅ **Easy maintenance** - changes in one place

├── build_voucher_plan_item()      # Abstract - implement in subclass- ✅ **Fast extensions** - new voucher types in ~100 lines

└── Common logic (600+ lines):- ✅ **Consistent behavior** - all scripts follow same flow

    ├── Data loading- ✅ **Time savings** - master script processes all types at once

    ├── Voucher number generation
    ├── Markdown generation
    ├── SevDesk API interaction
    └── CLI argument parsing
```

Each specialized creator (Gehalt, ÜLP, Spenden, etc.) inherits from `VoucherCreatorBase` and implements only the transaction-specific logic.

**Benefits:**
- 38% code reduction (2452 → 910 lines)
- Consistent behavior across all voucher types
- Easy to add new voucher types
- Single place to fix bugs or add features

### Master Orchestrator

`create_all_vouchers.py` provides:
- Single command to process all voucher types
- Smart data reload caching (75% time savings)
- Unified markdown report with summary table
- Consistent CLI interface across all types

## Development

### Adding a New Voucher Type

1. Create new script in `scripts/vouchers/`:
```python
from src.vouchers.voucher_creator_base import VoucherCreatorBase

class MyVoucherCreator(VoucherCreatorBase):
    def get_script_name(self) -> str:
        return "My Voucher Type"
    
    def filter_transactions(self, transactions: List[Dict]) -> List[Dict]:
        # Implement filtering logic
        return filtered_transactions
    
    def build_voucher_plan_item(self, transaction: Dict, voucher_number: str) -> Dict:
        # Implement voucher building logic
        return voucher_item

if __name__ == "__main__":
    creator = MyVoucherCreator()
    creator.run()
```

2. Add to `create_all_vouchers.py`:
```python
from scripts.vouchers.my_new_voucher import MyVoucherCreator

# In MasterVoucherCreator.__init__:
self.creators.append(("🆕", MyVoucherCreator()))
```

### Running Tests

```bash
# Future: Unit tests will be added to tests/ directory
pytest tests/
```

## Documentation

- **[REFACTORING_SUMMARY.md](docs/REFACTORING_SUMMARY.md)** - Details of the refactoring process
- **[MASTER_VOUCHER_CREATOR_DOCS.md](docs/MASTER_VOUCHER_CREATOR_DOCS.md)** - Master script documentation
- **[MASTER_SCRIPT_COMPLETE.md](docs/MASTER_SCRIPT_COMPLETE.md)** - Implementation completion notes

## Performance

**Before refactoring:**
- Running all 6 voucher types: ~3 minutes (6x data reload)
- Total code: 2452 lines across 6 scripts

**After refactoring:**
- Running all 6 voucher types: ~45 seconds (1x data reload)
- Total code: 910 lines (38% reduction)
- Time savings: 75%

## License

[Your License Here]

## Contributing

[Contributing guidelines if needed]
