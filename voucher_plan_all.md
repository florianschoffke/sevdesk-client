# 📋 Unified Voucher Plan - All Types

**Generated:** 2025-10-22 08:59:13
**Total Vouchers:** 5

## 📊 Summary by Type

| Icon | Type | Count | Accounting Type | Status |
|------|------|-------|-----------------|--------|
| 💰 | Gehalt (Salaries) | 4 | Lohn / Gehalt | ✅ Ready |
| 🎓 | ÜLP (Übungsleiterpauschale) | 0 | Ehrenamtspauschale/Übungsleiterpauschale | ⚪ None |
| 💝 | Spenden (Donations) | 1 | Spendeneingang | ✅ Ready |
| 🏥 | Krankenkassen (Health Insurance) | 0 | Krankenkasse | ⚪ None |
| ⛪ | Grace Baptist | 0 | Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke | ⚪ None |
| 🌍 | Kontaktmission | 0 | Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke | ⚪ None |
| 📚 | EBTC (Donations) | 0 | Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke | ⚪ None |
| 🏕️ | JEK Freizeit | 0 | Durchlaufende Posten | ⚪ None |
| 🏦 | Geldtransit | 0 | Geldtransit | ⚪ None |
| 💳 | Fees | 0 | Kontoführung / Kartengebühren | ⚪ None |

**Total:** 5 vouchers across 2 types

## 💰 Gehalt (Salaries)

**Count:** 4 vouchers
**Accounting Type:** Lohn / Gehalt (ID: 58)

| # | Date | Amount | Payee/Payer | Purpose | Cost Centre | Contact |
|---|------|--------|-------------|---------|-------------|---------|
| 1 | 2025-10-21 | €-520.00 | GWENDOLYN RUTH DEWHURST | Gehalt 10/2025 PNR 00110 | ✅ Gwen Dewhurst | ✅ |
| 2 | 2025-10-21 | €-556.00 | Samuel JeanRichard-dit-Bressel | Gehalt 10/2025 PNR 00113 | ✅ Samuel Jeanrichard ( | ✅ |
| 3 | 2025-10-21 | €-1,591.50 | Jonathan de Vries | Gehalt 10/2025 PNR 00108 | ✅ Jonathan de Vries | ✅ |
| 4 | 2025-10-21 | €-520.00 | THOMAS HOCHSTETTER | Gehalt 10/2025 PNR 00109 | ✅ Thomas Hochstetter | ✅ |

*See individual plan file: `voucher_plan_gehalt.md`*

## 💝 Spenden (Donations)

**Count:** 1 vouchers
**Accounting Type:** Spendeneingang (ID: 935667)

| # | Date | Amount | Donor | Purpose | Type | Cost Centre | Contact |
|---|------|--------|-------|---------|------|-------------|---------|
| 1 | 2025-10-21 | €450.00 | Thomas Hochstetter, Nina Hochs | Spende | 💝 general | ✅ Spendeneingänge Kont | ✅ |

*See individual plan file: `voucher_plan_spenden.md`*

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
python3 scripts/vouchers/create_vouchers_for_gehalt.py --create-all  # 💰 Gehalt (Salaries)
python3 scripts/vouchers/create_vouchers_for_spenden.py --create-all  # 💝 Spenden (Donations)
```
