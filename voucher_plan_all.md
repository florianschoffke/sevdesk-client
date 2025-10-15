# 📋 Unified Voucher Plan - All Types

**Generated:** 2025-10-15 16:46:08
**Total Vouchers:** 18

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
| 🏦 | Bankeinzug | 18 | Geldtransit | ✅ Ready |

**Total:** 18 vouchers across 1 types

## 🏦 Bankeinzug

**Count:** 18 vouchers
**Accounting Type:** Geldtransit (ID: 40)

| # | Transaction ID | Date | Amount | Payee/Payer | Cost Centre | Contact |
|---|----------------|------|--------|-------------|-------------|---------|
| 1 | 1781148672 | 2025-09-02 | €101.86 | Bankeinzug | ❌ | ✅ |
| 2 | 1778187796 | 2025-08-20 | €98.59 | Bankeinzug | ❌ | ✅ |
| 3 | 1773989958 | 2025-08-02 | €104.49 | Bankeinzug | ❌ | ✅ |
| 4 | 1765721277 | 2025-07-02 | €94.45 | Bankeinzug | ❌ | ✅ |
| 5 | 1758424050 | 2025-06-02 | €98.18 | Bankeinzug | ❌ | ✅ |
| 6 | 1750910942 | 2025-05-02 | €98.59 | Bankeinzug | ❌ | ✅ |
| 7 | 1747674278 | 2025-04-16 | €25.00 | Bankeinzug | ❌ | ✅ |
| 8 | 1746183228 | 2025-04-10 | €116.95 | Bankeinzug | ❌ | ✅ |
| 9 | 1743867571 | 2025-04-02 | €74.60 | Bankeinzug | ❌ | ✅ |
| 10 | 1743586314 | 2025-04-02 | €103.06 | Bankeinzug | ❌ | ✅ |
| 11 | 1735734472 | 2025-03-02 | €107.21 | Bankeinzug | ❌ | ✅ |
| 12 | 1728537047 | 2025-02-02 | €107.32 | Bankeinzug | ❌ | ✅ |
| 13 | 1727125127 | 2025-01-27 | €107.14 | Bankeinzug | ❌ | ✅ |
| 14 | 1727125125 | 2025-01-27 | €12.39 | Bankeinzug | ❌ | ✅ |
| 15 | 1727125123 | 2025-01-27 | €12.39 | Bankeinzug | ❌ | ✅ |
| 16 | 1727125121 | 2025-01-27 | €12.39 | Bankeinzug | ❌ | ✅ |
| 17 | 1726381576 | 2025-01-23 | €1,527.00 | Bankeinzug | ❌ | ✅ |
| 18 | 1719519149 | 2025-01-02 | €107.38 | Bankeinzug | ❌ | ✅ |

*See individual plan file: `voucher_plan_bankeinzug.md`*

## ⚠️ Warnings

- ⚠️  **Bankeinzug**: 18 voucher(s) without cost centre

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
python3 create_vouchers_for_bankeinzug.py --create-all  # 🏦 Bankeinzug
```
