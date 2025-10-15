# 📋 Unified Voucher Plan - All Types

**Generated:** 2025-10-15 09:11:45
**Total Vouchers:** 4

## 📊 Summary by Type

| Icon | Type | Count | Accounting Type | Status |
|------|------|-------|-----------------|--------|
| 💰 | Gehalt (Salaries) | 0 | Lohn / Gehalt | ⚪ None |
| 🎓 | ÜLP (Übungsleiterpauschale) | 0 | Ehrenamtspauschale/Übungsleiterpauschale | ⚪ None |
| 💝 | Spenden (Donations) | 0 | Spendeneingang | ⚪ None |
| 🏥 | Krankenkassen (Health Insurance) | 4 | Krankenkasse | ✅ Ready |
| ⛪ | Grace Baptist | 0 | Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke | ⚪ None |
| 🌍 | Kontaktmission | 0 | Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke | ⚪ None |

**Total:** 4 vouchers across 1 types

## 🏥 Krankenkassen (Health Insurance)

**Count:** 4 vouchers
**Accounting Type:** Krankenkasse (ID: 57)

| # | Transaction ID | Date | Amount | Payee/Payer | Cost Centre | Contact |
|---|----------------|------|--------|-------------|-------------|---------|
| 1 | 1738457926 | 2025-03-11 | €233.33 | Techniker Krankenkasse | ✅ Lohnnebenkosten | ✅ |
| 2 | 1731701292 | 2025-02-12 | €161.03 | Knappschaft-Bahn-See | ✅ Lohnnebenkosten | ✅ |
| 3 | 1731701289 | 2025-02-12 | €166.40 | Knappschaft-Bahn-See | ✅ Lohnnebenkosten | ✅ |
| 4 | 1731701285 | 2025-02-12 | €93.33 | Techniker Krankenkasse | ✅ Lohnnebenkosten | ✅ |

*See individual plan file: `voucher_plan_krankenkassen.md`*

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
python3 create_vouchers_for_krankenkassen.py --create-all  # 🏥 Krankenkassen (Health Insurance)
```
