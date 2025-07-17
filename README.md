### **Projekt‑ und Datenbeschreibung**


## 1  |  Klinischer Kontext, Auftrag & Zielsetzung

| Punkt                                 | Inhalt                                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Auftraggeber**                      |                                                                                                                                                                                                                                                                                                                          |
| **Hauptproblem**                      | Immunsupprimierte Patient\*innen (= oncology, transplant, autoimmune under B/T‑cell depletion) können **prolonged / persistent SARS‑CoV‑2 infections** (POI) entwickeln, deren Standardtherapie (5 Tage Nirmatrelvir + Ritonavir, NMV‑r) häufig nicht genügt.                                                                                                                                    |
| **Population of Interest (POI)**      | 104 Einzelfälle aus der Literatur, die **alle** bereits eine **verlängerte** NMV‑r‑Therapie (≥ 10 Tage oder ≥ 2 Kurse) als Zweit‑ oder Spätlinie erhalten haben.                                                                                                                                                                                                                                 |
| **Zentrale Analysefragen**            | 1) **Welche Erstlinientherapie** erhielten diese Patient*innen vor der Verlängerung?<br>2) **Wie häufig** kamen die vier Grundpfade (NMV‑r Yes/No × Other Antiviral Yes/No) in … <br>  • der Gesamtkohorte POI (n = 104) und <br>  • der Subkohorte **sPOI mono** (n = 29) = Patient*innen, die in der Zweitlinie *ausschließlich* verlängertes NMV‑r (ohne Kombinationspartner) erhielten, vor? |
| **Deliverable (Meeting 15 Jul 2025)** | **Genau eine Test‑Grafik** – ein Sankey/Snake‑Diagramm, das die Erstlinienpfade für POI 104 und sPOI‑mono 29 zeigt. **Keine** weiteren Tabellen, Analysen oder Zeitachsen, bis die Grafik intern abgenommen ist.                                                                                                                                                                                 |
| **Frist**                             | PNG + PDF bis **Montag­abend** (erstes Review).                                                                                                                                                                                                                                                                                                                                                  |

---

## 2  |  Datei **data characteristics v3.xlsx** – Vollständige Struktur

### 2.1  |  Worksheet‑Übersicht

| Sheet‑Name *(original)* | Kurzlabel     | Patientenzeilen        | Einsatz im aktuellen Arbeitsauftrag                                            |
| ----------------------- | ------------- | ---------------------- | ------------------------------------------------------------------------------ |
| `Included studies`      | *Included*    | 0 (reine Meta‑Tabelle) | **Ignorieren** (Literatur­verzeichnis)                                         |
| `POI, n=104`            | **POI**       | **104**                | **Haupt­eingabe für Grafik**                                                   |
| `sPOI mono, n=29`       | **sPOI‑mono** | **29**                 | **zweites Teil‑Panel**                                                         |
| `sPOI combo, n=56`      | *sPOI‑combo*  | 56                     | **vorerst ignorieren** (wird evtl. später für Mono‑vs‑Combo‑Analysen benötigt) |

*Alle weiteren Blätter oder Hidden‑Sheets wurden am 15 Jul 2025 überprüft – keine relevanten Daten jenseits dieser vier Sheets.*

### 2.2  |  Wichtigste Metadaten‑Fakten aus dem Meeting

* **Spalten­header** entsprechen weiterhin den **Langtiteln** der Erstversion; **keine** internen Kürzel wie `nmv1_yes` existieren.
* **Zeilenaufbau**: Die ersten 2–3 Zeilen enthalten Überschriften / Erläuterungen; **ab Zeile 4** beginnt die Datentabelle.
* **Leere Zwischenzeilen**: Teilweise zur visuellen Trennung der Studienberichte – **müssen** beim Import gefiltert werden (`first author` ≠ NA).
* **Keine Spalten­umbenennungen** wurden seit Meeting vorgenommen; dies bleibt Aufgabe der Datenaufbereitung im Skript.

---

## 3  |  Datendictionary (extrahiert aus POI‑Sheet, gilt analog für sPOI‑mono / combo)

|    Nr. | Original‑Spaltenname *(Zeile 3 der XLSX)*          | Typ               | Relevanz für **Sankey**   | Kommentar                                   |
| -----: | -------------------------------------------------- | ----------------- | ------------------------- | ------------------------------------------- |
|     01 | `first author\n(year)`                             | string            | nein                      | Literaturquelle, zugleich *Not‑NULL‑Filter* |
|     …  | *(Demografie‑ & Basis‑Variablen, #02–#14)*         | siehe alte README | nein                      | für später                                  |
|     15 | `previous antiviral drugs (days) / [dosage]`       | string            | **ja ("Other AV")**       | ‎`≠ "none"` → Yes                           |
|     16 | `any glucocorticosteroid usage …`                  | string            | nein                      | Meeting: *Glukokortikoide ignorieren*       |
|     17 | `any previous NMV-r treatment …`                   | string            | **ja ("NMV‑r 1st line")** | Werte `yes` / `no`                          |
|     18 | `form of therapy [mono / combination]`             | string            | nein (für *Testgrafik*)   | 2nd Line‑Klassifikation                     |
|     19 | `standard duration NMV-r treatment courses [n]`    | int               | potentiell                | Markierung der 1st‑Line‑Intensität          |
|     20 | `total days of extended NMV-r treatment [courses]` | int               | nein                      | gehört zur Zweit‑/Spätlinie                 |
|     21 | `concomitant antiviral therapy (days) / [dosages]` | string            | **ja ("Other AV")**       | zusätzl. Flag für „Other AV“                |
|  22–27 | *Outcomes & Comments*                              | string/int        | nein                      | für spätere Analysen                        |

> **Praktisches Mapping für die Grafik**
>
> ```text
> NMVr_1L = (any previous NMV-r treatment …) == "yes"
> OtherAV_1L = (previous antiviral drugs … ≠ "none") OR
>              (concomitant antiviral therapy … ≠ "none")
> ```

---

## 4  |  Sankey‑/Snake‑Diagramm – Detail‑Spezifikation

| Attribut              | Vorgabe (laut Meeting)                                                     |
| --------------------- | -------------------------------------------------------------------------- |
| **Panels**            | Panel A = POI (n = 104) • Panel B = sPOI‑mono (n = 29)                     |
| **Knoten links**      | „NMV‑r 1st Line: Yes“ / „No“                                               |
| **Knoten rechts**     | „Other antiviral 1st Line: Yes“ / „No“                                     |
| **Flows (4 Stück)**   | Yes/Yes • Yes/No • No/Yes • No/No                                          |
| **Breite**            | proportional zu absoluten **n**                                            |
| **Label jedes Flows** | `n = XX (YY %)` – YY gerundet auf ganze Prozent                            |
| **Farbpalette**       | Okabe‑Ito (color‑blind‑safe) – evtl. Graustufen für No/No                  |
| **Grafikformat**      | PNG (300 dpi, Breite ≥ 16 cm) *und* editierbares PDF                       |
| **Dateinamen**        | `figure_POI_Sankey_test.png` / `.pdf`                                      |
| **Review‑Prozess**    | Dr. Farokhnia annotiert Screenshot → Feedback‑Call                         |
| **Anmerkungen**       | *Keine* Kaplan‑Meier‑Achsen, *kein* Venn‑Hybrid; reine Flow‑Visualisierung |

---

## 5  |  Reproduzierbarer Workflow (Minimal‑Scope)

### 5.1  Datenextraktion (separate README‑Ergänzung)

*Wird von einem dedizierten Skript‑Autor umgesetzt; siehe Prompt 1.*

1. **Ziel**: CSV‑Exports „as‑is“ (POI, sPOI‑mono, sPOI‑combo).
2. **Kontrolle**: Zeilenzahl vs. Sheet‑N.
3. **Output**: `POI_n104_raw.csv`, `sPOI_mono_n29_raw.csv`, `sPOI_combo_n56_raw.csv`.

### 5.2  Minimal‑Cleaning & Feature‑Derivation

| Schritt            | Umsetzung (Framework‑agnostisch)                                                                |
| ------------------ | ----------------------------------------------------------------------------------------------- |
| **Import**         | CSVs in R / Python (pandas).                                                                    |
| **Zeilenfilter**   | `first author` ≠ NA.                                                                            |
| **Trim**           | Leerzeichen in *allen* Zellen & Spaltennamen.                                                   |
| **Binary Flags**   | `NMVr_firstline` (Yes/No) aus Spalte 17;<br>`OtherAV_firstline` (Yes/No) aus Spalten 15 und 21. |
| **Fehlende Werte** | Unklare / leere Felder → `"unknown"`; im Sankey nicht angezeigt.                                |
| **Duplikate**      | Prüfung auf `study specific case/patient ID`; Duplikate **nur markieren**, nicht löschen.       |

### 5.3  Aggregieren für Sankey

```text
Group by  NMVr_firstline, OtherAV_firstline
Count     n
Compute   %  = n / 104   (Panel A)  |   29 (Panel B)
```


---

## 6  |  Frequently Asked Implementation Questions

| Frage                                               | Kurzantwort                                                                                     |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| **Muss die sPOI‑combo‑Gruppe irgendwo auftauchen?** | **Nein** – erst nach Abnahme der Test‑Grafik diskutieren.                                       |
| **Glukokortikoide, Outcomes, Extended Days?**       | Für diese Grafik **irrelevant**; bleiben im Datensatz ungenutzt.                                |
| **Warum zwei Panels statt vier Grafiken?**          | Wunsch Auftraggeber: direkte Nebeneinander‑Vergleichbarkeit von Gesamt‑ vs. Mono‑Subkohorte.    |
| **Prozentbasis für sPOI‑mono?**                     | **29** Fälle sind 100 %; keine Hochrechnung auf 104.                                            |
| **Ist ein Code‑Lockfile nötig?**                    | Nicht gefordert; Coding kann in beliebiger Umgebung erfolgen, solange PNG & PDF lieferbar sind. |

---

## 7  |  Nächste Schritte (ausschließlich aus Meeting & Mail)

1. **CSV‑Export (Prompt 1)** – *Sofort ausführen.*
2. **Minimal‑Cleaning & Flag‑Ableitung** – über ein zweites Skript oder Notebook.
3. **Erstellen der Test‑Sankey‑Grafik** nach Spezifikation.
4. **Versand Montagabend** an Dr. Farokhnia.
5. **Feedback‑Termin** → ggf. Farb‑ oder Label‑Feintuning.
6. **Erst nach Freigabe**: Entscheidung, ob

   * Zweitlinien‑Mono vs Kombi‑Grafik,
   * Outcome‑Analysen,
   * oder PRISMA/Forest‑Plots erstellt werden.

*(Alle weiterführenden Analysen sind ausdrücklich **vertagt**.)*

---

## 8  |  Optional – Dokumentations‑Best‑Practice (nicht Teil des aktuellen Auftrags)

| Empfehlung               | Begründung                                                                                      |
| ------------------------ | ----------------------------------------------------------------------------------------------- |
| **Codebook (YAML/JSON)** | erleichtert späteres Mapping der Langheader auf handlichere Variablennamen.                     |
| **renv / virtualenv**    | garantiert Reproduzierbarkeit von Plot‑Farben & Layout in Folge‑Analysen.                       |
| **PRISMA‑Diagramm**      | das Sheet *Included* liefert bereits Autor + n – kann später halb‑automatisch generiert werden. |
| **Versionierung**        | Namenskonvention `figure_POI_Sankey_v01.png` → Feedback → v02 …                                 |

---

## 9  |  Take‑Home‑Message (One‑Pager)

> **Aufgabe:**
> Erzeuge **eine** farbenblind‑taugliche Sankey‑Grafik, die für **POI (104 Fälle)** und **sPOI‑mono (29 Fälle)** zeigt, ob Patient\*innen in der Erstlinie NMV‑r und/oder andere Antiviralia erhalten haben. Alles weitere (Mono vs Kombi, Outcomes, Publikations‑Tabellen) wird **erst nach** Sichtung und Freigabe dieser Testgrafik definiert.

---

*Prepared by: Clinical Biostatistics | File version: README\_v4 | Last update: 15 Jul 2025*

