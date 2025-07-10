### **Projekt‑ und Datenbeschreibung (Langfassung, vollständig replizierbar)**

---

#### 1  |  Ausgangssituation & Ziel

* **Auftraggeber**: Aresh (Mail an Kia).
* **Fragestellung**: Für eine Individual‑Patient‑Data‑(IPD‑)Analyse zu **lang andauernden bzw. rezidivierenden SARS‑CoV‑2‑Infektionen** unter *nirmatrelvir + ritonavir* (NMV‑r) sollen **anschauliche, publikationsreife Grafiken** („schöne, verständliche Bildli“) erstellt werden.
* **Schwerpunkt‑Visualisierung**: Ein **Snake‑Diagramm / Sankey‑Flow**, das den **Prozess‑ bzw. Subgruppen‑Überlapp** zwischen

  1. NMV‑r‑Erstlinientherapie (Ja / Nein) und
  2. zusätzlicher Einsatz **anderer antiviraler Medikamente** (Ja / Nein)
     im Gesamtkollektiv (**POI, n = 104**) und in der **Subpopulation sPOI mono (n = 29)** abbildet.
* **Komplexitätsniveau**: Keine ausgefallenen Statistik‑Plots, sondern klar strukturierte, visuell selbsterklärende Abbildungen im Stil des mitgelieferten Screenshots (Figure 3).

---

#### 2  |  Excel‑Datei **data characteristics v2.xlsx** – Struktur

| Ordner    | Datei                            | Relevanz         | Inhalt in Kurzform                  |
| --------- | -------------------------------- | ---------------- | ----------------------------------- |
| /mnt/data | **data characteristics v2.xlsx** | Arbeitsgrundlage | 4 Worksheets (Sheets) – siehe unten |

##### 2.1  |  Worksheet‑Übersicht

| Sheet‑Name (Original) | Kurzbezeichnung | Zeilenzahl (roh) | Patientenzeilen (≙ nicht‑leere Spalte *first author*) | Zweck im Projekt                                                |
| --------------------- | --------------- | ---------------- | ----------------------------------------------------- | --------------------------------------------------------------- |
| `' Included studies'` | **Included**    | …                | 0                                                     | Literatur‑/Studien­übersicht – **vorerst ignorieren**           |
| `'POI, n=104'`        | **POI**         | 160              | **104**                                               | **Hauptkohorte** aller Patienten mit ≥1 NMV‑r‑Behandlung        |
| `'sPOI mono, n=29'`   | **sPOI mono**   | 31               | **29**                                                | Unterkohorte mit **monotherapeutischem** NMV‑r‑Einsatz          |
| `'sPOI combo, n=56'`  | **sPOI combo**  | 58               | 56                                                    | Unterkohorte mit **Kombinationstherapien** – aktuell ignorieren |

> **Hinweis**: Zeilen > Patientenzahl enthalten Leerzeilen oder Zwischenüberschriften und müssen bei der Auswertung gefiltert werden (z. B. `df[df['first author\n(year)'].notna()]`).

##### 2.2  |  Spaltenlayout der Patientensheets (POI / sPOI)

Die Spalten sind in **28 (POI)** bzw. **25 (sPOI mono)** Felder gegliedert. Bis auf zwei führende Leer‑Spalten (`Unnamed: 0/1`) sind alle Variablen in **Row 3 (0‑basiert: index 2)** sauber benannt.

| Index | Spaltenname (Original)                             | Datentyp       | Beschreibung / Kodierung                               |
| ----- | -------------------------------------------------- | -------------- | ------------------------------------------------------ |
| 2     | `first author\n(year)`                             | string         | Literaturquelle des Fallberichts                       |
| 3     | `patients with extended NMV-r [n]`                 | int/float      | Anzahl Pat. pro Studie mit verlängerter NMV‑r‑Therapie |
| 4     | `Baseline disease cohort …`                        | string (a/m/t) | **a**utoimmun / **m**alignancy / **t**ransplant        |
| 5     | `study specific case/patient ID number`            | string/int     | Fall‑ID innerhalb der Publikation                      |
| 6     | `sex [male, female]`                               | string (m/f)   | Geschlecht                                             |
| 7     | `age`                                              | int            | Alter in Jahren                                        |
| 8     | `baseline disease`                                 | string         | Grunderkrankung (Freitext)                             |
| 9     | `baseline therapy`                                 | string         | Immunsuppressiva, Chemotherapie etc.                   |
| 10    | `vaccination [yes / no] (doses) ?`                 | string         | “y (3)” = geimpft, 3 Dosen                             |
| 11    | `hospitalization [yes / no] ?`                     | string         | Stationäre Aufnahme ja/nein                            |
| 12    | `SARS-CoV-2 genotype`                              | string         | Pango‑Lineage, z. B. BA.5                              |
| 13    | `CT lung changes [yes / no] ?`                     | string         | COVID‑typische CT‑Befunde ja/nein                      |
| 14    | `SARS-CoV-2 replication [days]`                    | int            | Dauer positiver PCR                                    |
| 15    | `previous antiviral drugs (days) / [dosage]`       | string         | z. B. “RDV 5 d”                                        |
| 16    | `any glucocorticosteroid usage …`                  | string         | Steroidgabe ja/nein                                    |
| 17    | `any previous NMV-r treatment …`                   | string         | Frühere NMV‑r‑Zyklen                                   |
| 18    | `form of therapy [mono / combination]`             | string         | **mono** vs. **combination**                           |
| 19    | `standard duration NMV-r treatment courses [n]`    | int            | Anzahl regulärer 5‑Tage‑Zyklen                         |
| 20    | `total days of extended NMV-r treatment [courses]` | int            | Gesamtdauer aller Verlängerungen                       |
| 21    | `concomitant antiviral therapy (days) / [dosages]` | string         | Mitbehandlung (RDV, ENS, etc.)                         |
| 22    | `any adverse events [yes / no] ?`                  | string         | Unerwünschte Ereignisse                                |
| 23    | `type of adverse event`                            | string         | z. B. „GI toxicity”                                    |
| 24    | `eradication outcome successful …`                 | string         | Viruselimination ja/nein                               |
| 25    | `survival outcome [yes / no] ?`                    | string         | Überlebt ja/nein                                       |
| 26    | `eradication/treatment response …`                 | string         | **c**linical / **v**irological / **r**adiological      |
| 27    | `comments`                                         | string         | Freitext                                               |

*(POI enthält 28, sPOI mono 25 Spalten; in sPOI fehlen die beiden Zähl‑Spalten \[Index 3 und 19] und evtl. Leer‑Spalten.)*

---

#### 3  |  Benötigte Grafiken

| # | Visualisierung                                | Datengrundlage        | Zweck                                                                                                                                                              |
| - | --------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1 | **Sankey / Snake‑Diagramm** (analog Figure 3) | **POI 104 Pat.**      | Vier Flanken: *linke Seite* = „Any NMV‑r (yes/no)“; *rechte Seite* = „Other antiviral drugs (yes/no)“. Breitenproportionaler Fluss zeigt Frequenzen & Überlappung. |
| 2 | **Sankey / Snake‑Diagramm**                   | **sPOI mono 29 Pat.** | Gleiches Layout, aber Beschränkung auf Monotherapie‑Fälle (form of therapy = mono).                                                                                |
| 3 | (Optional) **Vergleichsdiagramm**             | POI vs. sPOI mono     | Balken‑ oder gestapelte Säulen, um prozentuale Verteilung der 4 Kombinationen hervorzuheben.                                                                       |

**Darstellungs‑Specs (einheitlich für alle Plots)**

* **Format**: PNG (300 dpi) **und** PDF (Vektor)
* **Farben**: Farbblind‑freundliche Palette, Links/Rechts klar unterscheidbar, Flows in Grau‑Stufen ► Fokus auf Kategorien, nicht auf Farbe.
* **Beschriftung**: Achsenfrei; Legende mit absoluter Zahl **+ Prozent**; Titel im Stil: “First‑line treatment strategies with NMV‑r and other antivirals – POI (n = 104)”.
* **Code‑Reproduzierbarkeit**: Datencleaning‑Schritte (Filter, Typ‑Konvertierung) klar in einem Skript dokumentieren.

---

#### 4  |  Workflow (Schritt‑für‑Schritt, replizierbar)

1. **Import & Cleaning**

   * `read_excel(..., header=2)` für POI und `header=1` für sPOI mono.
   * Entfernen der Leer‑Spalten `Unnamed: 0/1`.
   * Zeilenfilter: nur Datensätze mit nicht‑leerem `first author\n(year)`.
   * Normalisierung der Ja/Nein‑Angaben (`y|yes` → `Yes`, `n|no|NaN` → `No`).

2. **Variable derivation**

   * `NMVr_firstline` = **Yes**, wenn `any previous NMV-r treatment` == `No` **und** `form of therapy` enthält NMV‑r.
   * `Other_AV` = **Yes**, wenn `concomitant antiviral therapy…` nicht leer **oder** `previous antiviral drugs…` nicht NaN.
   * Prüfen der Definition mit Fachexperten, ggf. Code‑Book ergänzen.

3. **Summary‑Table** (Basis für Sankey)

   ```text
   NMVr_firstline | Other_AV | n | %
   ---------------|----------|---|---
   Yes            | Yes      |   |
   Yes            | No       |   |
   No             | Yes      |   |
   No             | No       |   |
   ```

   * Prozentwerte relativ zur jeweiligen Population (104 / 29).

4. **Plot‑Erstellung**

   * Python‑Pakete: `pandas`, `plotly` oder `matplotlib + pySankey`.
   * Knotenreihenfolge fixieren: linke Knoten („No“, „Yes“), rechte Knoten („No“, „Yes“).
   * Flussbreite = `n`.
   * Label‑Format: “No (71%, 74)” etc.

5. **Export & Qualitäts‑Check**

   * Auflösung prüfen (≥ 300 dpi), Achsen/Ränder abschneiden, Dateinamen:
     `sankey_POI_104.png`, `sankey_sPOI_mono_29.png`, `...pdf`.
   * Peer‑Review durch Aresh, ggf. Farbanpassungen.

---

#### 5  |  Kontext für spätere Erweiterungen

* **Included‑Sheet** enthält die bibliographischen Metadaten der Quellstudien – nützlich für PRISMA‑Flowcharts, derzeit aber nicht Teil des Auftrags.
* **sPOI combo (n = 56)** könnte in einem zweiten Schritt analog ausgewertet werden (Vergleich Mono vs. Kombi).
* Variablen wie `eradication outcome` & `survival outcome` bieten Potenzial für Kaplan‑Meier‑Plots oder Forest‑Plots, falls in späteren Analysen benötigt.

---

#### 6  |  Ergebnis

Diese Dokumentation liefert eine **vollständige, eindeutige Spezifikation** des Datenbestands, der Variablen, der gewünschten Visualisierungen und der notwendigen Verarbeitungsschritte. Eine statistisch versierte Person kann damit **ohne Einsicht in die ursprüngliche Mail oder den Screenshot** das Projekt nachvollziehen und die geforderten Grafiken exakt erstellen.
