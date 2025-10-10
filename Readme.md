# SevDesk Transaction Manager# SevDesk Transaction Manager# SevDesk Transaction Manager



A Python-based tool to manage SevDesk transactions and automate voucher creation using SQLite database.



## FeaturesA Python-based tool to manage SevDesk transactions and automate voucher creation using SQLite database.A Python-based tool to manage SevDesk transactions and automate voucher creation using SQLite database.



### Transaction Management

- Fetch open transactions from SevDesk API

- Store transactions in SQLite database## Features## Features

- Search and filter transactions



### Voucher Creation

- **Automated voucher creation** for different transaction types### Transaction Management### Transaction Management

- **Master orchestrator** to run all voucher types at once

- **6 specialized voucher creators**:- Fetch open transactions from SevDesk API- Fetch open transactions from SevDesk API

  - 💰 Gehalt (Salaries)

  - 🎓 ÜLP (Übungsleiterpauschale)- Store transactions in SQLite database- Store transactions in SQLite database

  - 💝 Spenden (Donations)

  - 🏥 Krankenkassen (Health Insurance)- Search and filter transactions- Search and filter transactions

  - ⛪ Grace Baptist Donations

  - 🌍 Kontaktmission Donations- Bulk edit transactions- Bulk edit transactions

- **Unified markdown reports** with summary tables

- **Batch processing** for time savings (75% faster)



## Quick Start### Voucher Creation### Voucher Creation (NEW!)



```bash- **Automated voucher creation** for different transaction types- **Automated voucher creation** for different transaction types

# 1. Install dependencies

pip install -r requirements.txt- **Master orchestrator** to run all voucher types at once- **Master orchestrator** to run all voucher types at once



# 2. Configure API credentials- **6 specialized voucher creators**:- **6 specialized voucher creators**:

cp .env.example .env

# Edit .env and add your SevDesk API key  - 💰 Gehalt (Salaries)  - 💰 Gehalt (Salaries)



# 3. Load data  - 🎓 ÜLP (Übungsleiterpauschale)  - 🎓 ÜLP (Übungsleiterpauschale)

python3 scripts/loaders/reload_data.py

  - 💝 Spenden (Donations)  - 💝 Spenden (Donations)

# 4. Create vouchers

python3 create_all_vouchers.py  - 🏥 Krankenkassen (Health Insurance)  - 🏥 Krankenkassen (Health Insurance)

```

  - ⛪ Grace Baptist Donations  - ⛪ Grace Baptist Donations

## Usage

  - 🌍 Kontaktmission Donations  - 🌍 Kontaktmission Donations

### Master Voucher Script (Recommended!)

- **Unified markdown reports** with summary tables- **Unified markdown reports** with summary tables

**Run from project root - super convenient!**

- **Batch processing** for time savings- **Batch processing** for time savings

```bash

# Generate plan

python3 create_all_vouchers.py

## Setup## Setup

# Test mode

python3 create_all_vouchers.py --create-single



# Create all1. Install dependencies:1. Install dependencies:

python3 create_all_vouchers.py --create-all

``````bash```bash



### Individual Voucher Scriptspip install -r requirements.txtpip install -r requirements.txt



```bash``````

python3 scripts/vouchers/create_vouchers_for_spenden.py

python3 scripts/vouchers/create_vouchers_for_gehalt.py

# etc.

```2. Create `.env` file with your SevDesk API credentials:2. Create `.env` file with your SevDesk API credentials:



### Load Data```bash```bash



```bashcp .env.example .envcp .env.example .env

# Reload everything

python3 scripts/loaders/reload_data.py# Edit .env and add your API key# Edit .env and add your API key



# Or load specific data``````

python3 scripts/loaders/load_transactions.py

python3 scripts/loaders/load_contacts.py

```

3. Reload data from SevDesk:3. Run the transaction loader:

## Project Structure

```bash```bash

```

.python3 scripts/loaders/reload_data.pypython load_transactions.py

├── create_all_vouchers.py        # 👈 Convenience wrapper - run from here!

├── src/                          # Library code``````

│   ├── sevdesk/                  # API client

│   ├── database/                 # Database operations

│   └── vouchers/                 # Framework

├── scripts/                      ## Project Structure## Project Structure

│   ├── loaders/                  # Data loading

│   └── vouchers/                 # Voucher creators

├── docs/                         # Documentation

├── reports/                      # Generated plans``````

└── transactions.db               # Database

```..



## Documentation├── src/                          # Core library code├── sevdesk/                      # SevDesk API client module



- **[AUTOMATION_OPPORTUNITIES.md](docs/AUTOMATION_OPPORTUNITIES.md)** - Analysis: 183 transactions could be automated!│   ├── sevdesk/                  # SevDesk API client│   ├── __init__.py

- **[REFACTORING_SUMMARY.md](docs/REFACTORING_SUMMARY.md)** - How we reduced code by 38%

- **[RESTRUCTURING.md](docs/RESTRUCTURING.md)** - Project reorganization details│   │   ├── __init__.py│   └── client.py



## Performance│   │   └── client.py├── database/                     # Database operations



- **Time savings:** 75% (3min → 45sec for all voucher types)│   ├── database/                 # Database operations│   ├── __init__.py

- **Code reduction:** 38% (2452 → 910 lines)

- **Automation rate:** 13% currently, 45-50% possible│   │   ├── __init__.py│   └── db.py



## Automation Opportunities│   │   └── db.py├── voucher_creator_base.py       # Base class for voucher creators (NEW!)



**Current Status:** 27/210 transactions automated (12.9%)│   └── vouchers/                 # Voucher creation framework├── create_all_vouchers.py        # Master orchestrator for all vouchers (NEW!)



**High-Priority Opportunities:**│       ├── __init__.py├── create_vouchers_for_*.py      # Individual voucher creators (NEW!)

1. **Auslage** (Expense Reimbursements) - 33 transactions

2. **JEK Freizeit** (Youth Events) - 18 transactions  │       ├── voucher_creator_base.py   # Base class (Template Method Pattern)├── voucher_utils.py              # Shared voucher utilities (NEW!)

3. **QM Support** (Recurring Service) - 10 transactions

4. **Miete** (Rent) - 3 transactions worth €30,000!│       └── voucher_utils.py          # Shared utilities├── load_transactions.py          # Load transactions from API



See [AUTOMATION_OPPORTUNITIES.md](docs/AUTOMATION_OPPORTUNITIES.md) for full analysis.├── scripts/                      # Executable scripts├── reload_data.py                # Reload all data from API



## Architecture│   ├── loaders/                  # Data loading scripts├── requirements.txt              # Python dependencies



Built with **Template Method Pattern** for code reuse:│   │   ├── load_transactions.py├── .env.example                  # Example environment variables

- Base class handles all common logic (600+ lines)

- Subclasses implement only specific filtering/mapping│   │   ├── load_contacts.py├── REFACTORING_SUMMARY.md        # Refactoring documentation (NEW!)

- Result: Consistent, maintainable, extensible

│   │   ├── load_categories.py├── MASTER_VOUCHER_CREATOR_DOCS.md # Master script docs (NEW!)

## Contributing

│   │   ├── load_cost_centres.py└── README.md                     # This file

To add a new voucher type, create a subclass of `VoucherCreatorBase` and implement:

- `get_script_name()` - Display name│   │   ├── load_accounting_types.py```

- `filter_transactions()` - Which transactions to process

- `build_voucher_plan_item()` - How to build the voucher│   │   └── reload_data.py        # Reload all data



See [MASTER_VOUCHER_CREATOR_DOCS.md](docs/MASTER_VOUCHER_CREATOR_DOCS.md) for details.│   └── vouchers/                 # Voucher creation scripts## Usage


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
