# 📋 Unified Voucher Plan - All Types

**Generated:** 2025-10-17 15:00:29
**Total Vouchers:** 9

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
| 💳 | Fees | 9 | Kontoführung / Kartengebühren | ✅ Ready |

**Total:** 9 vouchers across 1 types

## 💳 Fees

**Count:** 9 vouchers
**Accounting Type:** Kontoführung / Kartengebühren (ID: 74)

| # | Date | Amount | Payee/Payer | Purpose | Cost Centre | Contact |
|---|------|--------|-------------|---------|-------------|---------|
| 1 | 2025-09-30 | €-42.58 | Unknown | Saldo der Abschlussposten QM - Support 0 | ✅ Buchführung, Bankgeb | ✅ |
| 2 | 2025-08-31 | €-36.14 | Unknown | Saldo der Abschlussposten QM - Support 0 | ✅ Buchführung, Bankgeb | ✅ |
| 3 | 2025-07-31 | €-38.66 | Unknown | Saldo der Abschlussposten QM - Support 0 | ✅ Buchführung, Bankgeb | ✅ |
| 4 | 2025-06-30 | €-42.02 | Unknown | Saldo der Abschlussposten QM - Support 0 | ✅ Buchführung, Bankgeb | ✅ |
| 5 | 2025-05-30 | €-40.34 | Unknown | Saldo der Abschlussposten QM - Support 0 | ✅ Buchführung, Bankgeb | ✅ |
| 6 | 2025-04-30 | €-49.30 | Unknown | Saldo der Abschlussposten QM - Support 0 | ✅ Buchführung, Bankgeb | ✅ |
| 7 | 2025-03-31 | €-40.90 | Unknown | Saldo der Abschlussposten QM - Support 0 | ✅ Buchführung, Bankgeb | ✅ |
| 8 | 2025-02-28 | €-39.78 | Unknown | Saldo der Abschlussposten QM - Support 0 | ✅ Buchführung, Bankgeb | ✅ |
| 9 | 2025-01-31 | €-37.54 | Unknown | Saldo der Abschlussposten QM - Support 0 | ✅ Buchführung, Bankgeb | ✅ |

*See individual plan file: `voucher_plan_fees.md`*

## 🚀 Next Steps

### Option 1: Create All Vouchers at Once
```bash
# Test with one voucher per type
python3 create_all_vouchers.py --create-single

# Create ALL vouchers for ALL types
python3 create_all_vouchers.py --create-all
```

### Option 2: Create by Individual Type
```bash
python3 create_vouchers_for_fees.py --create-all  # 💳 Fees
```
