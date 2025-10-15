# EBTC Voucher Creator Documentation

## Overview

The EBTC Voucher Creator automatically processes outgoing donation transactions to EBTC (Europäisches Bibel Trainings Centrum e.V.).

## Configuration

- **Accounting Type:** Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke
- **Cost Centre:** Spendenausgänge
- **Transaction Type:** Outgoing (negative amounts / expenses)

## Matching Criteria

The script finds transactions that match ALL of the following:

1. **Amount < 0** (outgoing payment)
2. **"EBTC"** in payee name OR payment purpose
3. **"Spende"** or **"SPENDE"** in payment purpose

## Usage

### 1. Generate Voucher Plan

```bash
python3 scripts/vouchers/create_vouchers_for_ebtc.py
```

This generates `voucher_plan_ebtc.md` with all matching transactions.

### 2. Create Single Test Voucher

```bash
python3 scripts/vouchers/create_vouchers_for_ebtc.py --create-single
```

Creates only the first voucher for testing.

### 3. Create All Vouchers

```bash
python3 scripts/vouchers/create_vouchers_for_ebtc.py --create-all
```

Creates vouchers for all matching transactions.

## Example Transaction

```
Transaction ID: 1789678938
Date: 2025-10-01
Amount: €-40.00
Payee: EBTC Europäisches Bibel Trainings Centrum e.V.
Purpose: SEPA-Dauerauftrag an Ihre Referenz: NOTPROVIDED SPENDE IBAN:...
Status: Open (100)
```

**Matches because:**
- ✅ Negative amount (outgoing payment)
- ✅ "EBTC" in payee name
- ✅ "SPENDE" in payment purpose

## Integration with Master Script

EBTC is automatically included when running the master voucher creator:

```bash
python3 create_all_vouchers.py
```

This processes EBTC along with all other voucher types (Gehalt, ÜLP, Spenden, etc.).

## Notes

- EBTC donations are **outgoing** (expenses), unlike "Spenden" which are **incoming** (revenue)
- Uses the same accounting type as Grace Baptist and Kontaktmission
- Contact is automatically matched to "EBTC Europaeisches Bibel Trainings Centrum e.V." in SevDesk
- Typically €40.00 monthly recurring donations

## Related Documentation

- [VoucherCreatorBase](../src/vouchers/voucher_creator_base.py) - Base class documentation
- [Master Voucher Creator](MASTER_VOUCHER_CREATOR_DOCS.md) - Unified voucher processing
- [Voucher Plans](../voucher_plan_ebtc.md) - Generated plans
