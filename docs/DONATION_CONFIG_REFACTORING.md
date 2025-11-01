# Donation Voucher Configuration Refactoring - Complete

## Summary

Successfully refactored the donation voucher creation script to use an external CSV configuration file instead of hardcoded matching logic.

## Changes Made

### 1. Created Configuration System

**New file:** `config/donation_rules.csv`
- Comprehensive CSV file with all donation matching rules
- Supports filter rules (identify donations) and type rules (categorize donations)
- Includes all existing hardcoded rules migrated to CSV format
- Well-commented with inline documentation

### 2. Refactored `scripts/vouchers/create_vouchers_for_spenden.py`

**New features:**
- `DonationRule` class: Represents a single matching rule with pattern matching logic
- Dynamic rule loading from CSV file on script startup
- Flexible pattern matching with three modes:
  - `contains`: Pattern appears anywhere in text (default)
  - `startswith`: Text must start with pattern
  - `exact`: Text must exactly match pattern

**Modified methods:**
- `__init__()`: Now loads rules from CSV file
- `_load_donation_rules()`: New method to parse CSV and build rule lists
- `find_accounting_type()`: Dynamically loads cost centres based on CSV rules
- `filter_transactions()`: Uses CSV filter rules instead of hardcoded conditions
- `_determine_donation_type_and_cost_centre()`: Uses priority-ordered type rules from CSV

### 3. Created Documentation

**New file:** `config/DONATION_RULES_README.md`
- Complete guide to the CSV configuration format
- Examples for all rule types and match modes
- Priority system explanation
- Troubleshooting guide
- Step-by-step instructions for adding new rules

## How It Works

### Filter Rules
```csv
filter,,Spende,,,100,contains
```
- If ANY filter rule matches, transaction is treated as a donation
- Can match on payer name, purpose, or both

### Type Rules
```csv
type,,Artur Jeske,jeske,Jeske (Durchlaufende Posten),10,contains
type,,,general,Spendeneingänge Konto,1000,contains
```
- Rules checked in priority order (lower number = higher priority)
- FIRST matching rule determines donation type and cost centre
- Should always have a catch-all rule (priority 1000)

## Current Rules Migrated

### Filter Rules (12 rules)
- Spende / SPENDE
- Tobi Zimmermann
- Unterstützung / Unterstuetzung
- Gemeindespende
- für die Gemeinde
- MONATLICHE SPENDE
- GEMEINDE / GEMEINDE SPENDE
- Spends / Offering
- Monatsspende (startswith)

### Type Rules (6 rules)
1. Priority 10: Artur Jeske → Jeske (Durchlaufende Posten)
2. Priority 20: Tobias Zimmermann donations → Tobias Zimmermann (Spende für Tobias)
3. Priority 30: Mission/Missionar → Spendeneingänge Missionare
4. Priority 1000: Catch-all → Spendeneingänge Konto (general)

## Benefits

1. **No Code Changes Needed**: Add/modify donation rules by editing CSV file
2. **More Flexible**: Support for payer name matching, not just purpose
3. **Priority System**: Control rule evaluation order explicitly
4. **Multiple Match Modes**: Choose exact, contains, or startswith matching
5. **Better Maintainability**: Rules are data, not code
6. **Easy Testing**: Modify CSV and re-run without code changes
7. **Self-Documenting**: CSV file includes inline comments and examples

## Usage

### View Current Configuration
```bash
cat config/donation_rules.csv
```

### Add New Donation Keyword
Edit `config/donation_rules.csv` and add:
```csv
filter,,NEW_KEYWORD,,,100,contains
```

### Add Specific Donor Rule
```csv
type,Max Mustermann,,special,Special Cost Centre,15,exact
```

### Test Changes
```bash
python3 scripts/vouchers/create_vouchers_for_spenden.py
```
Review the generated plan in `reports/voucher_plan_spenden.md`

### Create Vouchers
```bash
python3 scripts/vouchers/create_vouchers_for_spenden.py --create-all
```

## Migration Notes

- All existing hardcoded rules have been preserved
- Behavior should be identical to previous version
- CSV file includes detailed comments explaining each rule
- README file provides comprehensive documentation

## Files Created/Modified

### Created
- `config/donation_rules.csv` - Rule configuration file
- `config/DONATION_RULES_README.md` - Documentation

### Modified
- `scripts/vouchers/create_vouchers_for_spenden.py` - Refactored to use CSV

## Next Steps

You can now easily:
1. Add new donation keywords by adding filter rules
2. Create special handling for specific donors by adding high-priority type rules
3. Modify donation categorization without touching code
4. Test different rule configurations quickly

## Example: Adding a New Rule

Let's say you want to match "Building Fund" donations to a special cost centre:

1. Add filter rule (if needed):
```csv
filter,,Building Fund,,,100,contains
```

2. Add type rule with high priority:
```csv
type,,Building Fund,building,Building Fund Cost Centre,15,contains
```

3. Re-run the script to test

That's it! No code changes needed.
