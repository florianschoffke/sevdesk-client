# 📋 Unified Voucher Plan - All Types

**Generated:** 2025-10-21 18:55:53
**Total Vouchers:** 7

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
| 🏦 | Geldtransit | 7 | Geldtransit | ✅ Ready |
| 💳 | Fees | 0 | Kontoführung / Kartengebühren | ⚪ None |

**Total:** 7 vouchers across 1 types

## 🏦 Geldtransit

**Count:** 7 vouchers
**Accounting Type:** Geldtransit (ID: 40)

| # | Date | Amount | Payee/Payer | Purpose | Cost Centre | Contact |
|---|------|--------|-------------|---------|-------------|---------|
| 1 | 2025-10-03 | €-101.60 | PayPal (Europe) S.a r.l. et Ci | 1045235637049 PP.4871.PP . Atlassian US, | ❌ | ✅ |
| 2 | 2025-04-22 | €-25.00 | PayPal (Europe) S.a r.l. et Ci | 1041590456354 PP.4871.PP . Apple Service | ❌ | ✅ |
| 3 | 2025-04-11 | €-116.95 | PayPal (Europe) S.a r.l. et Ci | 1041460164638 PP.4871.PP . Qustodio Tech | ❌ | ✅ |
| 4 | 2025-01-29 | €-107.14 | PayPal (Europe) S.a r.l. et Ci | 1039893118320 PP.4871.PP . The Good Book | ❌ | ✅ |
| 5 | 2025-01-29 | €-12.39 | PayPal (Europe) S.a r.l. et Ci | 1039892903113 PP.4871.PP . Buchhandlung  | ❌ | ✅ |
| 6 | 2025-01-29 | €-12.39 | PayPal (Europe) S.a r.l. et Ci | 1039892883338 PP.4871.PP . Buchhandlung  | ❌ | ✅ |
| 7 | 2025-01-29 | €-12.39 | PayPal (Europe) S.a r.l. et Ci | 1039892819100 PP.4871.PP . Buchhandlung  | ❌ | ✅ |

*See individual plan file: `voucher_plan_geldtransit.md`*

## ⚠️ Warnings

- ⚠️  **Geldtransit**: 7 voucher(s) without cost centre

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
python3 scripts/vouchers/create_vouchers_for_geldtransit.py --create-all  # 🏦 Geldtransit
```
