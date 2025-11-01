# Donation Rules Configuration

This file explains how to configure donation matching rules in `config/donation_rules.csv`.

## Overview

The donation voucher creator uses an external CSV file to determine:
1. **Which transactions are donations** (filter rules)
2. **What type of donation** and which cost centre to use (type rules)

This allows you to manage donation matching logic without modifying code.

## CSV File Format

The CSV file has the following columns:

| Column | Description | Required |
|--------|-------------|----------|
| `rule_type` | Either `filter` or `type` | Yes |
| `payer_name_pattern` | Pattern to match against payer name | No (leave empty to skip) |
| `purpose_pattern` | Pattern to match against payment purpose | No (leave empty to skip) |
| `donation_type` | Type of donation (e.g., mission, general, jeske, tobias) | Only for `type` rules |
| `cost_centre_name` | Name of cost centre to use | Only for `type` rules |
| `priority` | Lower number = higher priority (checked first) | Yes |
| `match_mode` | How to match: `contains`, `startswith`, or `exact` | Yes (default: contains) |

## Rule Types

### Filter Rules (`rule_type=filter`)

Filter rules determine if a transaction should be treated as a donation.

- If **any** filter rule matches, the transaction is considered a donation
- You can match on payer name, purpose, or both
- Leave `donation_type` and `cost_centre_name` empty for filter rules

**Example:**
```csv
rule_type,payer_name_pattern,purpose_pattern,donation_type,cost_centre_name,priority,match_mode
filter,,Spende,,,100,contains
filter,,MONATLICHE SPENDE,,,100,contains
filter,John Doe,,,,90,contains
```

### Type Rules (`rule_type=type`)

Type rules determine which donation type and cost centre to use for matched donations.

- Rules are checked in **priority order** (lower number = checked first)
- The **first matching rule** is used
- You should have a **catch-all rule** with high priority (e.g., 1000) as fallback

**Example:**
```csv
rule_type,payer_name_pattern,purpose_pattern,donation_type,cost_centre_name,priority,match_mode
type,,Artur Jeske,jeske,Jeske (Durchlaufende Posten),10,contains
type,,Mission,mission,Spendeneingänge Missionare,30,contains
type,,,general,Spendeneingänge Konto,1000,contains
```

## Match Modes

### `contains` (default)
Pattern appears anywhere in the text.
```csv
filter,,Spende,,,100,contains
```
Matches: "Spende", "Gemeindespende", "MONATLICHE SPENDE"

### `startswith`
Text must start with the pattern.
```csv
filter,,Monatsspende,,,100,startswith
```
Matches: "Monatsspende 01/2024", but not "Erste Monatsspende"

### `exact`
Text must exactly match the pattern.
```csv
filter,,SPENDE,,,100,exact
```
Matches: "SPENDE", but not "Spende" or "SPENDEN"

## Pattern Matching Logic

For each rule:
- If `payer_name_pattern` is specified, it must match the payer name
- If `purpose_pattern` is specified, it must match the payment purpose
- If **both** are specified, **both** must match
- If neither is specified, the rule always matches (useful for catch-all rules)

## Priority System

Type rules use priority to determine matching order:

1. **Priority 1-50**: High priority, specific rules (e.g., specific people or purposes)
2. **Priority 51-500**: Medium priority, category rules (e.g., mission-related)
3. **Priority 500+**: Low priority, catch-all rules

**Important:** Always include a catch-all rule with high priority number (e.g., 1000) to handle donations that don't match specific rules.

## Complete Example

```csv
# Filter rules - determine if transaction is a donation
rule_type,payer_name_pattern,purpose_pattern,donation_type,cost_centre_name,priority,match_mode
filter,,Spende,,,100,contains
filter,,Unterstützung,,,100,contains
filter,,Offering,,,100,contains
filter,Mustermann Max,,,,90,contains

# Type rules - determine donation type and cost centre
rule_type,payer_name_pattern,purpose_pattern,donation_type,cost_centre_name,priority,match_mode
type,,Artur Jeske,jeske,Jeske (Durchlaufende Posten),10,contains
type,Max Mustermann,,special,Spezialspenden,15,exact
type,,Tobias Zimmermann,tobias,Tobias Zimmermann (Spende für Tobias),20,contains
type,,Mission,mission,Spendeneingänge Missionare,30,contains
type,,Missionar,mission,Spendeneingänge Missionare,30,contains
type,,,general,Spendeneingänge Konto,1000,contains
```

## Adding New Rules

### To add a new donation keyword:

Add a filter rule:
```csv
filter,,NEW_KEYWORD,,,100,contains
```

### To add a new donation type:

1. Add a type rule with appropriate priority:
```csv
type,,PURPOSE_PATTERN,new_type,Cost Centre Name,25,contains
```

2. Make sure the cost centre exists in SevDesk

### To handle a specific donor:

Add a high-priority type rule with payer name:
```csv
type,Donor Name,,special,Special Cost Centre,5,exact
```

## Testing

After modifying the CSV file:

1. Run the script in plan mode (default):
   ```bash
   python3 scripts/vouchers/create_vouchers_for_spenden.py
   ```

2. Check the generated plan in `reports/voucher_plan_spenden.md`

3. Verify:
   - All expected donations are matched
   - Donation types are correct
   - Cost centres are assigned properly

## Troubleshooting

### "No matching type rule" warning
- Add more specific type rules OR
- Verify your catch-all rule (priority 1000) is present

### Transaction not detected as donation
- Add or modify filter rules to match the transaction
- Check payer name and purpose for patterns

### Wrong cost centre assigned
- Check rule priorities (lower number = checked first)
- Add more specific rules with lower priority numbers
- Verify cost centre names match exactly what's in SevDesk

## Notes

- CSV file is loaded when the script starts
- Lines starting with `#` are ignored (comments)
- Empty lines are ignored
- Pattern matching is **case-sensitive** by default
- Use both uppercase and lowercase patterns if needed (e.g., "Spende" and "SPENDE")
