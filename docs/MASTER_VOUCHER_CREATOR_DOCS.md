# Master Voucher Creator - Dokumentation

## Überblick

Das **Master Voucher Creator Script** (`create_all_vouchers.py`) orchestriert alle einzelnen Voucher-Erstellungs-Scripts und bietet eine zentrale Schnittstelle für:

1. **Unified Planning** - Übersicht über alle Voucher-Typen in einem Markdown-Report
2. **Batch Creation** - Erstellen aller Vouchers auf einmal
3. **Consolidated Summary** - Gesamtstatistik über alle Voucher-Typen

## Verwendung

### 1. Unified Plan generieren (Standard)

```bash
python3 create_all_vouchers.py
```

**Effekt:**
- Läuft durch alle 6 Voucher-Typen
- Sammelt alle offenen Transaktionen
- Generiert `voucher_plan_all.md` mit:
  - Summary-Tabelle nach Typ
  - Detaillierte Voucher-Listen pro Typ
  - Gesamtstatistik

**Output:**
```
📋 UNIFIED VOUCHER PLAN GENERATED
✓ Plan saved to: voucher_plan_all.md

Summary by Type:
Icon   Type                                Count    Status
----------------------------------------------------------------------
💰     Gehalt (Salaries)                   5        ✅ Ready
🎓     ÜLP (Übungsleiterpauschale)        3        ✅ Ready
💝     Spenden (Donations)                15       ✅ Ready
🏥     Krankenkassen (Health Insurance)   2        ✅ Ready
⛪     Grace Baptist                       0        ⚪ None
🌍     Kontaktmission                      1        ✅ Ready
----------------------------------------------------------------------
TOTAL                                      26
```

### 2. Test-Modus (ein Voucher pro Typ)

```bash
python3 create_all_vouchers.py --create-single
```

**Effekt:**
- Generiert Plan wie oben
- Erstellt **1 Voucher pro Typ** (Test-Modus)
- Vergleichbar mit `--create-single` der einzelnen Scripts
- Perfekt zum Testen der gesamten Pipeline

**Use Case:**
- Vor dem ersten Produktiv-Lauf testen
- Neue Accounting-Typen verifizieren
- API-Verbindung prüfen

### 3. Alle Vouchers erstellen

```bash
python3 create_all_vouchers.py --create-all
```

**Effekt:**
- Generiert Plan wie oben
- Fragt nach Bestätigung
- Erstellt **ALLE Vouchers** für **ALLE Typen**
- Zeigt Fortschritt für jeden Typ
- Verifiziert Transaction-Status nach Erstellung

**Use Case:**
- Monatlicher Batch-Run
- Alle offenen Transaktionen auf einmal verarbeiten
- Zeit sparen (anstatt 6 einzelne Scripts)

## Generated Output

### voucher_plan_all.md

Strukturierte Markdown-Datei mit:

```markdown
# 📋 Unified Voucher Plan - All Types

**Generated:** 2025-10-10 09:07:11
**Total Vouchers:** 26

## 📊 Summary by Type

| Icon | Type | Count | Accounting Type | Status |
|------|------|-------|-----------------|--------|
| 💰 | Gehalt (Salaries) | 5 | Lohn / Gehalt | ✅ Ready |
| 🎓 | ÜLP (Übungsleiterpauschale) | 3 | Ehrenamtspauschale | ✅ Ready |
...

## 💰 Gehalt (Salaries)

**Count:** 5 vouchers
**Accounting Type:** Lohn / Gehalt (ID: 58)

| # | Transaction ID | Date | Amount | Payee/Payer | Cost Centre | Contact |
|---|----------------|------|--------|-------------|-------------|---------|
| 1 | 123456 | 2025-10-01 | €2,500.00 | John Doe | ✅ John Doe | ✅ |
...

## 💝 Spenden (Donations)

**Count:** 15 vouchers
**Accounting Type:** Spendeneingang (ID: 935667)

| # | Transaction ID | Date | Amount | Donor | Type | Cost Centre | Contact |
|---|----------------|------|--------|-------|------|-------------|---------|
| 1 | 789012 | 2025-10-05 | €100.00 | Jane Smith | 💝 general | ✅ Spendeneingänge | ✅ |
...

## 🚀 Next Steps

### Option 1: Create All Vouchers at Once
```bash
python3 create_all_vouchers.py --create-single  # Test
python3 create_all_vouchers.py --create-all     # Production
```

### Option 2: Create by Individual Type
```bash
python3 create_vouchers_for_gehalt.py --create-all
python3 create_vouchers_for_spenden.py --create-all
...
```
```

## Voucher-Typen

Das Master-Script orchestriert diese 6 Voucher-Typen:

| Icon | Type | Script | Description |
|------|------|--------|-------------|
| 💰 | Gehalt | `create_vouchers_for_gehalt.py` | Gehalt (Salaries) |
| 🎓 | ÜLP | `create_vouchers_for_ulp.py` | Übungsleiterpauschale |
| 💝 | Spenden | `create_vouchers_for_spenden.py` | Spenden (Donations) |
| 🏥 | Krankenkassen | `create_vouchers_for_krankenkassen.py` | Health Insurance |
| ⛪ | Grace Baptist | `create_vouchers_for_grace_baptist.py` | Grace Baptist Donations |
| 🌍 | Kontaktmission | `create_vouchers_for_kontaktmission.py` | Kontaktmission Donations |

## Workflow

### Interner Ablauf

```
1. MasterVoucherCreator.run()
   ↓
2. run_all_creators()
   ↓
   For each voucher type:
   ├── Instantiate Creator Class
   ├── Load Environment
   ├── Reload Data (once, cached)
   ├── Initialize API Client
   ├── Open Database
   ├── Find Accounting Type
   ├── Get & Filter Transactions
   ├── Generate Voucher Plan
   └── Store Result
   ↓
3. generate_unified_markdown()
   ├── Create Summary Table
   ├── Create Detailed Sections
   └── Save to voucher_plan_all.md
   ↓
4. print_summary()
   └── Console Output
   ↓
5. create_all_vouchers() [if --create-single or --create-all]
   ├── Confirm with User
   ├── For each type with vouchers:
   │   ├── Create Vouchers
   │   ├── Book to Transactions
   │   └── Verify Status
   └── Print Final Summary
```

### Optimierungen

1. **Data Reload einmal** - Daten werden nur beim ersten Creator-Lauf geladen, dann cached
2. **Parallele Planung** - Alle Voucher-Pläne werden gleichzeitig erstellt
3. **Gemeinsame DB-Verbindung** - Effiziente Datenbanknutzung

## Vorteile gegenüber einzelnen Scripts

### Zeitersparnis

**Vorher** (6 einzelne Scripts):
```bash
python3 create_vouchers_for_gehalt.py        # ~30s
python3 create_vouchers_for_ulp.py           # ~30s
python3 create_vouchers_for_spenden.py       # ~30s
python3 create_vouchers_for_krankenkassen.py # ~30s
python3 create_vouchers_for_grace_baptist.py # ~30s
python3 create_vouchers_for_kontaktmission.py # ~30s
---------------------------------------------------
Total: ~3 Minuten (6x Data Reload!)
```

**Nachher** (Master Script):
```bash
python3 create_all_vouchers.py               # ~45s
---------------------------------------------------
Total: ~45 Sekunden (1x Data Reload!)
```

**Zeitersparnis: ~2 Minuten (75%)**

### Übersicht

- ✅ **Ein Report** statt 6 separate Dateien
- ✅ **Gesamtstatistik** über alle Typen
- ✅ **Sortierte Darstellung** nach Voucher-Typ
- ✅ **Warnings** für alle Typen zentral

### Convenience

- ✅ **Ein Befehl** für alles
- ✅ **Batch-Creation** für alle Typen
- ✅ **Unified Testing** mit --create-single

## Beispiel-Workflow: Monatsabschluss

### Schritt 1: Übersicht verschaffen
```bash
python3 create_all_vouchers.py
# → Zeigt alle offenen Transaktionen gruppiert nach Typ
# → Generiert voucher_plan_all.md
```

### Schritt 2: Plan reviewen
```bash
open voucher_plan_all.md  # macOS
# oder
cat voucher_plan_all.md
```

**Prüfen:**
- Sind alle Typen erfasst? ✅
- Sind Cost Centres zugeordnet? ✅
- Sind Contacts gefunden? ✅
- Gibt es Warnings? ⚠️

### Schritt 3: Test-Run
```bash
python3 create_all_vouchers.py --create-single
# → Erstellt 1 Voucher pro Typ
# → Verifiziert API-Calls
# → Prüft Transaction-Verlinkung
```

### Schritt 4: Produktiv-Run
```bash
python3 create_all_vouchers.py --create-all
# → Erstellt ALLE Vouchers
# → Zeigt Fortschritt
# → Verifiziert Status
```

**Output:**
```
🚀 CREATING VOUCHERS FOR ALL TYPES
Mode: ALL vouchers

Will create vouchers for:
  💰 Gehalt (Salaries): 5 voucher(s)
  🎓 ÜLP (Übungsleiterpauschale): 3 voucher(s)
  💝 Spenden (Donations): 15 voucher(s)
  🏥 Krankenkassen (Health Insurance): 2 voucher(s)
  🌍 Kontaktmission: 1 voucher(s)

Total vouchers to create: 26

⚠️  Do you want to proceed? (y/N): y

... [Creation Progress] ...

🎉 ALL VOUCHER CREATION COMPLETED
✓ Successfully created: 26 voucher(s)
```

### Schritt 5: Verifizierung
```bash
# Prüfe in SevDesk:
# - Sind Vouchers erstellt?
# - Sind Transaktionen verlinkt?
# - Status korrekt?
```

## Error Handling

Das Master-Script fängt Fehler pro Voucher-Typ ab:

```python
❌ Error running Gehalt (Salaries): Connection timeout

Summary:
✅ ÜLP: 3 vouchers
❌ Gehalt: Error (Connection timeout)
✅ Spenden: 15 vouchers
...
```

→ Andere Typen werden **nicht** blockiert!

## Integration mit bestehenden Scripts

Das Master-Script **ersetzt nicht** die einzelnen Scripts!

**Beide Ansätze bleiben verfügbar:**

### Master-Script (Neu)
```bash
python3 create_all_vouchers.py [--create-single|--create-all]
```
**Use Case:** Batch-Processing, Übersicht, Zeitersparnis

### Einzelne Scripts (Bestehend)
```bash
python3 create_vouchers_for_gehalt.py [--create-single|--create-all]
```
**Use Case:** Fokus auf einen Typ, Detaillierte Kontrolle

## Technische Details

### Klassen-Hierarchie

```
MasterVoucherCreator
├── run_all_creators()
│   └── _run_single_creator()
│       └── GehaltVoucherCreator (extends VoucherCreatorBase)
│       └── UlpVoucherCreator (extends VoucherCreatorBase)
│       └── SpendenVoucherCreator (extends VoucherCreatorBase)
│       └── KrankenkassenVoucherCreator (extends VoucherCreatorBase)
│       └── GraceBaptistVoucherCreator (extends VoucherCreatorBase)
│       └── KontaktmissionVoucherCreator (extends VoucherCreatorBase)
├── generate_unified_markdown()
├── print_summary()
└── create_all_vouchers()
```

### State Management

```python
class MasterVoucherCreator:
    def __init__(self):
        self.results = []          # List of all results
        self.total_vouchers = 0    # Total vouchers found
        self.total_created = 0     # Total vouchers created
        self.total_failed = 0      # Total vouchers failed
        self._data_reloaded = False # Cache flag for data reload
```

### Result Structure

```python
{
    'key': 'gehalt',
    'icon': '💰',
    'name': 'Gehalt (Salaries)',
    'voucher_count': 5,
    'voucher_plan': [...],
    'creator': GehaltVoucherCreator(),
    'accounting_type': {...}
}
```

## Zukünftige Erweiterungen

### Mögliche Features

1. **Filtering** - Nur bestimmte Typen ausführen
   ```bash
   python3 create_all_vouchers.py --types gehalt,spenden
   ```

2. **JSON Export** - Maschinell lesbare Ausgabe
   ```bash
   python3 create_all_vouchers.py --format json
   ```

3. **Scheduling** - Automatischer Cron-Job
   ```bash
   # Täglich um 2 Uhr alle Vouchers erstellen
   0 2 * * * cd /path/to/project && python3 create_all_vouchers.py --create-all
   ```

4. **Email Notifications** - Bei Erfolg/Fehler
   ```python
   send_email(subject="Vouchers Created", body=summary)
   ```

5. **Dry-Run Mode** - Simulation ohne Erstellung
   ```bash
   python3 create_all_vouchers.py --dry-run
   ```

## Zusammenfassung

✅ **Ein Script** für alle Voucher-Typen  
✅ **Unified Report** mit Summary-Table  
✅ **Batch-Creation** für Zeitersparnis  
✅ **Test-Mode** für sichere Validierung  
✅ **Error-Resilient** - Fehler blockieren nicht andere Typen  
✅ **Kompatibel** mit bestehenden Scripts  

Das Master-Script ist das perfekte Tool für:
- 📊 Monats-/Quartalsabschlüsse
- 🚀 Batch-Processing von Transaktionen
- 📋 Übersichtliche Voucher-Verwaltung
- ⏱️ Zeitersparnis durch zentrale Orchestrierung
