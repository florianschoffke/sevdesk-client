# 📋 Unified Voucher Plan - All Types

**Generated:** 2025-10-31 21:37:49
**Total Vouchers:** 0

## 📊 Summary by Type

| Icon | Type | Count | Accounting Type | Status |
|------|------|-------|-----------------|--------|
| 💰 | Gehalt (Salaries) | 0 | Lohn / Gehalt | ⚪ None |
| 🎓 | ÜLP (Übungsleiterpauschale) | 0 | Ehrenamtspauschale/Übungsleiterpauschale | ⚪ None |
| 💝 | Spenden (Donations) | 0 | Spendeneingang | ⚪ None |
| 🏥 | Krankenkassen (Health Insurance) | 0 | Krankenkasse | ⚪ None |
| ⛪ | Grace Baptist | 0 | Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke | ⚪ None |
| 🌍 | Kontaktmission | 0 | Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke | ⚪ None |
| 📚 | EBTC (Donations) | 0 | Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke | ⚪ None |
| 🏕️ | JEK Freizeit | 0 | Durchlaufende Posten | ⚪ None |
| 🏦 | Geldtransit | 0 | Geldtransit | ⚪ None |
| 💳 | Fees | 0 | Kontoführung / Kartengebühren | ⚪ None |

**Total:** 0 vouchers across 0 types

## 🚀 Next Steps

### Option 1: Run Everything at Once
```bash
# Create ALL vouchers for ALL types AND mark Bar-Kollekten as paid
python3 scripts/vouchers/create_all_vouchers.py --run-all
```

### Option 2: Create Vouchers Only
```bash
# Test with one voucher per type
python3 scripts/vouchers/create_all_vouchers.py --create-single

# Create ALL vouchers for ALL types
python3 scripts/vouchers/create_all_vouchers.py --create-all
```

### Option 3: Create by Individual Type
```bash
```
