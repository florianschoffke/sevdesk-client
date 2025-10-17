# Bar-Kollekten Vouchers Without Cost Centre

**Total:** 48 voucher(s) need cost centre assignment

## Vouchers to Fix

These vouchers need to be assigned to the 'Bar-Kollekten' cost centre:

| # | Voucher ID | Date | Amount | Supplier | Description |
|---|------------|------|--------|----------|-------------|
| 1 | 124908147 | 2025-09-21 | €10.00 | Arol Djoufack | 456 |
| 2 | 124907852 | 2025-09-21 | €132.28 | Gemeinde | 455 |
| 3 | 124907647 | 2025-09-21 | €108.00 | Gemeinde | 454 |
| 4 | 124425662 | 2025-09-14 | €25.00 | Gemeinde | 432 |
| 5 | 124425589 | 2025-09-14 | €20.00 | Thomas Reich | 431 |
| 6 | 124425492 | 2025-09-14 | €124.00 | Gemeinde | 430 |
| 7 | 124425348 | 2025-09-14 | €175.00 | Gemeinde | 429 |
| 8 | 123961498 | 2025-09-07 | €100.00 | GIANG AN HUYNH | 428 |
| 9 | 123961436 | 2025-09-07 | €170.00 | Gemeinde | 427 |
| 10 | 123960947 | 2025-09-07 | €10.00 | Gemeinde | 426 |
| 11 | 123423045 | 2025-08-31 | €1.00 | Gemeinde | 425 |
| 12 | 123422937 | 2025-08-31 | €732.00 | Gemeinde | 424 |
| 13 | 123422860 | 2025-08-31 | €20.00 | Manfred Müller | 423 |
| 14 | 123422603 | 2025-08-31 | €20.00 | Thomas Reich | 421 |
| 15 | 122858532 | 2025-08-24 | €20.00 | Gemeinde | 420 |
| 16 | 122858492 | 2025-08-24 | €10.00 | Florian Schoffke | 419 |
| 17 | 122858394 | 2025-08-24 | €17.00 | Gemeinde | 418 |
| 18 | 122858194 | 2025-08-24 | €190.00 | Gemeinde | 417 |
| 19 | 122448460 | 2025-08-17 | €20.00 | Thomas Reich | 415 |
| 20 | 122448405 | 2025-08-17 | €307.50 | Gemeinde | 414 |
| 21 | 122448293 | 2025-08-10 | €10.00 | Florian Schoffke | 413 |
| 22 | 122448146 | 2025-08-10 | €20.00 | Thomas Reich | 412 |
| 23 | 122448035 | 2025-08-10 | €200.00 | Gemeinde | 411 |
| 24 | 122447885 | 2025-08-03 | €10.00 | Florian Schoffke | 410 |
| 25 | 122446245 | 2025-08-03 | €205.50 | Gemeinde | 409 |
| 26 | 122445284 | 2025-08-03 | €100.00 | Artur Jeske | 407 |
| 27 | 121120723 | 2025-07-27 | €20.00 | Gemeinde | 406 |
| 28 | 121120657 | 2025-07-27 | €160.00 | Gemeinde | 405 |
| 29 | 121120501 | 2025-07-27 | €175.00 | Gemeinde | 404 |
| 30 | 120398373 | 2025-07-20 | €10.00 | Gemeinde | 403 |
| 31 | 120398318 | 2025-07-20 | €20.00 | Christine Ziethen | 402 |
| 32 | 120398255 | 2025-07-20 | €20.00 | Florian Schoffke | 401 |
| 33 | 120398172 | 2025-07-20 | €20.00 | Thomas Reich | 400 |
| 34 | 120398117 | 2025-07-20 | €150.80 | Gemeinde | 399 |
| 35 | 120398040 | 2025-07-20 | €8.60 | Gemeinde | 398 |
| 36 | 120397944 | 2025-07-20 | €284.00 | Gemeinde | 397 |
| 37 | 120397904 | 2025-07-20 | €17.20 | Gemeinde | 396 |
| 38 | 120397809 | 2025-07-13 | €10.00 | Florian Schoffke | 395 |
| 39 | 120397759 | 2025-07-13 | €144.20 | Gemeinde | 394 |
| 40 | 120397676 | 2025-07-13 | €122.00 | Gemeinde | 393 |
| 41 | 120397344 | 2025-07-06 | €50.00 | Gemeinde | 390 |
| 42 | 120397265 | 2025-07-06 | €214.02 | Gemeinde | 389 |
| 43 | 120397188 | 2025-07-06 | €10.00 | Florian Schoffke | 388 |
| 44 | 120397123 | 2025-07-06 | €15.00 | Manfred Müller | 387 |
| 45 | 120397022 | 2025-07-06 | €216.00 | Gemeinde | 386 |
| 46 | 118009526 | 2025-06-22 | €20.00 | Thomas Reich | 375 |
| 47 | 103669226 | 2025-01-12 | €116.50 | Gemeinde | 560 |
| 48 | 99662550 | 2024-11-17 | €1.16 | Gemeinde | 504 |

**Total: 48 voucher(s) - €4,561.76**

## Next Steps

To fix these vouchers:

```bash
# Test with single voucher first:
python3 scripts/fix_bar_kollekten_cost_centre.py --fix-single

# Then fix all vouchers:
python3 scripts/fix_bar_kollekten_cost_centre.py --fix-all
```
