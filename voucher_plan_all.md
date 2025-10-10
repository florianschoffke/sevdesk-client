# 📋 Unified Voucher Plan - All Types

**Generated:** 2025-10-10 09:35:15
**Total Vouchers:** 2

## 📊 Summary by Type

| Icon | Type | Count | Accounting Type | Status |
|------|------|-------|-----------------|--------|
| 💰 | Gehalt (Salaries) | 0 | Lohn / Gehalt | ⚪ None |
| 🎓 | ÜLP (Übungsleiterpauschale) | 0 | Ehrenamtspauschale/Übungsleiterpauschale | ⚪ None |
| 💝 | Spenden (Donations) | 2 | Spendeneingang | ✅ Ready |
| 🏥 | Krankenkassen (Health Insurance) | 0 | Krankenkasse | ⚪ None |
| ⛪ | Grace Baptist | 0 | Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke | ⚪ None |
| 🌍 | Kontaktmission | 0 | Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke | ⚪ None |

**Total:** 2 vouchers across 1 types

## 💝 Spenden (Donations)

**Count:** 2 vouchers
**Accounting Type:** Spendeneingang (ID: 935667)

| # | Transaction ID | Date | Amount | Donor | Type | Cost Centre | Contact |
|---|----------------|------|--------|-------|------|-------------|---------|
| 1 | 1791578752 | 2025-10-10 | €100.00 | Juliane Reinhardt | 💝 general | ✅ Spendeneingänge Kont | ✅ |
| 2 | 1791578748 | 2025-10-09 | €80.00 | ERIKA BERGEN | 💝 general | ✅ Spendeneingänge Kont | ✅ |

*See individual plan file: `voucher_plan_spenden.md`*

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
python3 create_vouchers_for_spenden.py --create-all  # 💝 Spenden (Donations)
```
