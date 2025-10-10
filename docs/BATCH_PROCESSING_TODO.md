# Batch Processing TODO - Offene Transaktionen

**Stand:** 2025-10-09  
**Gesamt offene Transaktionen:** 296

---

## ✅ Bereits automatisiert

- [x] **Krankenkassen** (19 Transaktionen) - `create_vouchers_for_krankenkassen.py`
  - Techniker Krankenkasse
  - Knappschaft-Bahn-See
  - Cost Centre: Lohnnebenkosten

- [x] **Spenden** (0 aktuell offen) - `create_vouchers_for_spenden.py`
  - Spendeneinnahmen mit verschiedenen Typen
  - Cost Centres: Missionare, Allgemein, Jeske, Tobias

- [x] **Gehalt** (0 aktuell offen) - `create_vouchers_for_gehalt.py`
  - Gehaltsauszahlungen
  - Cost Centre: Lohn / Gehalt

- [x] **ÜLP** (0 aktuell offen) - `create_vouchers_for_ulp.py`
  - Übungsleiterpauschale / Ehrenamtspauschale
  - Cost Centre: Person-spezifisch

---

## 🔴 Priorität 1: Missions-Ausgaben (49 Transaktionen, -5.770€)

### KONTAKTMISSION DEUTSCHLAND (29 Transaktionen, -3.470€)

- [ ] **29 Transaktionen** von Januar bis Oktober 2025
- **Pattern:** Monatliche Daueraufträge
  - 100€ für Ehepaar Hodzi
  - 130€ für Jean Richards
  - 130€ für Familie Hodzi
- **Empfohlenes Skript:** `create_vouchers_for_kontaktmission.py`
- **Cost Centre:** Zu klären (wahrscheinlich "Missionare" oder "Spendeneingänge Missionare")
- **Accounting Type:** Zu klären
- **Contact:** KONTAKTMISSION DEUTSCHLAND

**Beispiel-Transaktionen:**
```
ID: 1719579051 | 2025-01-02 | -100.00€ | EHEPAAR HODZI
ID: 1720080333 | 2025-01-03 | -130.00€ | SPENDE FÜR JEAN RICHARDS
ID: 1720080331 | 2025-01-03 | -130.00€ | SPENDE FÜR FAM. HODZI
```

---

### GRACE BAPTIST TAMPERE RY (20 Transaktionen, -2.300€)

- [ ] **20 Transaktionen** von Januar bis Oktober 2025
- **Pattern:** Monatliche Daueraufträge für Miska Wilhelmsson
  - 100€ pro Monat
  - 130€ pro Monat (DONATION WILHELMSSON MONTHLY)
- **Empfohlenes Skript:** `create_vouchers_for_grace_baptist.py`
- **Cost Centre:** Zu klären (Mission nach Finnland)
- **Accounting Type:** Zu klären
- **Contact:** GRACE BAPTIST TAMPERE RY

**Beispiel-Transaktionen:**
```
ID: 1719579056 | 2025-01-02 | -100.00€ | SPENDE MISKA WILHELMSSON
ID: 1720080329 | 2025-01-03 | -130.00€ | DONATION WILHELMSSON MONTHLY
```

---

## 🟠 Priorität 2: EBTC Ausgaben (25 Transaktionen, -24.817€)

### EBTC Europäisches Bibel Trainings Centrum e.V. (25 Transaktionen)

- [ ] **25 Transaktionen** von Januar bis Oktober 2025
- **Pattern:** Mix aus verschiedenen Transaktionstypen
  - Monatliche Daueraufträge (2x 40€)
  - Rechnungen für Seminare/Unterstützung
  - Einzelspenden
- **Herausforderung:** Unterschiedliche Payee-Namen:
  - "EBTC Europäisches Bibel Trainings C entrum e.V."
  - "EBTC Europ. Bibel- Trainings Centru m e.V."
  - "EBTC"
- **Empfohlenes Skript:** `create_vouchers_for_ebtc.py`
- **Cost Centre:** Zu klären (evtl. "Schulungen" oder "Weiterbildung")
- **Accounting Type:** Zu klären
- **Contact Matching:** Alle Namen auf einen Contact mappen

**Beispiel-Transaktionen:**
```
ID: 1719579061 | 2025-01-02 | -40.00€ | SEPA-Dauerauftrag SPENDE
ID: 1722536959 | 2025-01-09 | -150.00€ | Spende Allgemein
ID: 1725799323 | 2025-01-21 | -125.00€ | Unterstützung Yilmaz Simsek, Seminar
ID: 1731394182 | 2025-02-12 | +240.00€ | Rueckerst. Doppelz. RG 210941
```

---

## 🟡 Priorität 3: Regelmäßige Vergütungen (20 Transaktionen, -2.781€)

### Jonathan de Vries (10 Transaktionen, -2.081€)

- [ ] **10 Transaktionen** von Februar bis Oktober 2025
- **Pattern:** Monatliche Zahlungen (unterschiedliche Beträge)
- **Empfohlenes Skript:** Evtl. in `create_vouchers_for_gehalt.py` integrieren
- **Cost Centre:** Zu klären
- **Accounting Type:** Zu klären

---

### Anna de Vries (10 Transaktionen, -700€)

- [ ] **10 Transaktionen** von Januar bis Oktober 2025
- **Pattern:** Monatliche Zahlungen (70€ pro Monat)
- **Empfohlenes Skript:** Evtl. in `create_vouchers_for_gehalt.py` integrieren
- **Cost Centre:** Zu klären
- **Accounting Type:** Zu klären

---

## 🟢 Priorität 4: Kleinere Batch-Gruppen

### diakonos e.K. (9 Transaktionen, -637€)

- [ ] **9 Transaktionen** von Januar bis September 2025
- **Pattern:** Regelmäßige Ausgaben
- **Cost Centre:** Zu klären
- **Accounting Type:** Zu klären

---

### PayPal Transaktionen (12 Transaktionen, -2.396€)

- [ ] **12 Transaktionen** verschiedene Monate
- **Herausforderung:** Gemischte Transaktionstypen
- **Empfehlung:** Manuell prüfen, evtl. nicht batch-fähig

---

### AMAZON PAYMENTS EUROPE S.C.A. (7 Transaktionen, -617€)

- [ ] **7 Transaktionen** verschiedene Monate
- **Cost Centre:** Zu klären
- **Accounting Type:** Zu klären

---

## 📊 Statistik nach Typ

| Typ | Anzahl | Summe |
|-----|--------|-------|
| Ausgabe (sonstige) | 117 | -90.459€ |
| Dauerauftrag | 88 | -7.900€ |
| Einnahme (sonstige) | 81 | +20.108€ |
| Spende | 10 | +10.552€ |

---

## 🎯 Nächste Schritte

1. **Sofort:** ÜLP-Skript anpassen (Ehrenamtspauschale hinzufügen)
2. **Kurzfristig:** KONTAKTMISSION und GRACE BAPTIST Skripte erstellen
3. **Mittelfristig:** EBTC Skript mit Contact-Mapping erstellen
4. **Langfristig:** Kleinere Gruppen evaluieren und ggf. automatisieren

---

## 💡 Hinweise

- Vor dem Erstellen neuer Skripte müssen **Cost Centres** und **Accounting Types** in der Datenbank geprüft werden
- Contact-Matching sollte fuzzy sein (siehe Krankenkassen-Beispiel)
- Alle Skripte sollten `voucher_utils.py` verwenden (refaktorierte Architektur)
- Belegnummern im Format **B-YYYY-NR** verwenden
