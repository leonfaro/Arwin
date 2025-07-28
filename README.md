### **Projekt‑ und Datenbeschreibung (Stand 28 Jul 2025)**

## 1  |  Klinischer Kontext, Auftrag & Zielsetzung
| Punkt | Inhalt |
|-------|--------|
| **Auftraggeber / Konsortium** | Multidisziplinäres Netzwerk aus Universitäts­kliniken (Hämatologie, Infektiologie, Transplantationsmedizin); Statistik‑Team UZH / Biostatistik |
| **Hauptproblem** | Immunsupprimierte Patient\*innen (onkologische, transplantierte, Autoimmun‑Erkrankte unter B‑/T‑Zell‑Depletion) entwickeln **prolonged / persistent SARS‑CoV‑2 infections** (POI), bei denen die Standard‑5‑Tage‑Therapie mit Nirmatrelvir + Ritonavir (NMV‑r, „Paxlovid“) häufig versagt |
| **Population of Interest (POI)** | **n = 104** Einzelfälle aus 25 Publikationen (2023–2024), die **alle** bereits eine **verlängerte** NMV‑r‑Therapie (≥ 10 Tage oder ≥ 2 Standardkurse) als Zweit‑ oder Spätlinie erhielten |
| **Hauptziel** | Testen, ob **verlängertes NMV‑r als Monotherapie** *nicht schlechter* ist als **verlängertes NMV‑r + zusätzliche Antivirale** (Kombination) bzgl. Virus‑Eradikation |
| **Primärer Endpunkt** | *Eradication_successful [yes/no]* – unverändert aus den Primärquellen übernommen |
| **Sekundäre Endpunkte** | • *any_adverse_events [yes/no]* + *type_of_adverse_event* (Sicherheit)  <br>• *SARS_CoV_2_replication_days* (Zeit bis PCR‑Negativität)  <br>• *survival_outcome [yes/no]* |
| **Haupt­hypothese** | Verlängerte NMV‑r‑Monotherapie erzielt in allen Basis­kohorten (maligne, Autoimmun, Transplant) vergleichbare Eradikations­raten wie Kombinations­therapie |

---

## 2  |  Studientyp & Datengrundlage
| Punkt | Inhalt |
|-------|--------|
| **Design** | Individual‑Patient‑Data (IPD) Meta‑Analyse (Fallserien / Case Reports) |
| **Datenquellen** | 25 peer‑reviewte Publikationen (siehe Variable *first_author_year*) |
| **Excel‑Workbook** | 3 Sheets → **primary_cohort** (n = 104), **subgroup_mono** (n = 33), **subgroup_combo** (n = 57) |
| **Kern­variablen** | *2nd_line_therapy_form*, *1st_line_standard_Paxlovid*, *1st_line_other_antiviral*, *2nd_line_extended_Paxlovid_total_days*, *eradication_successful*, *any_adverse_events*, *SARS_CoV_2_replication_days* u. a. |
| **Datenlücken (≥ 50 % Missing)** | *SARS_CoV_2_genotype* ≈ 51 %, *CT_lung_changes* ≈ 54 %, *type_of_adverse_event* ≈ 93 % |

---

## 3  |  Analyse‑ & Visualisierungskonzept

### Haupttext (max. 4 Grafiken)
| Fig | Titel & Inhalt | Datenspalten | Zweck |
|-----|----------------|--------------|-------|
| **1** | **Clustered Bar + 95 % CI** – Eradikation Mono vs Kombi | `2nd_line_therapy_form`, `eradication_successful` | Direktvergleich; Risk‑Difference & Risk Ratio annotiert |
| **2** | **Forest‑Plot** – Subgruppen‑OR (Malignancy / Autoimmune / Transplant / Mixed) | `Baseline_disease_cohort`, `2nd_line_therapy_form`, `eradication_successful` | Prüft Konsistenz der Haupt­hypothese |
| **3** | **Gestapeltes Balkendiagramm** – AE‑Profil | `2nd_line_therapy_form`, `any_adverse_events`, `type_of_adverse_event` | Sicherheits­vergleich |
| **4** | **Sankey‑Diagramm** – 1st‑Line Pfade → 2nd‑Line Form | `1st_line_standard_Paxlovid`, `1st_line_other_antiviral` (binarisiert), `2nd_line_therapy_form` | Kontextualisiert Therapie­wege |

### Supplement
| Fig S1 | **Heatmap** – Eradikation nach Paxlovid‑Dauer (10 | 11–21 | > 21 Tage) × Therapieform | `2nd_line_extended_Paxlovid_total_days` (binned), `2nd_line_therapy_form`, `eradication_successful` |

--

## 5  |  Limitationen
- Fallbericht‑Charakter; keine Randomisierung  
- Heterogene Definition „Eradikation“ (as reported)  
- > 50 % Missing bei Genotyp & CT → außerhalb der Hauptanalyse  
- Potenzielles Confounding in Therapie­wahl (Mono vs Kombi)  

---

## 6  |  Entscheidungsmatrix – Rückfragen & Antworten (26 Jul 2025)

| # | Rückfrage (Statistik‑Team) | Ärztliche Antwort | Einfluss auf Analysen |
|---|---------------------------|-------------------|-----------------------|
| 1 | Primärer Endpunkt? | **Virus‑Eradikation** | Fig 1–2 fokussieren auf Eradikation |
| 2 | Haupt­vergleich? | **Mono = Kombi (Nicht‑Unterlegenheit)** | Design aller Hauptfiguren |
| 3 | Subgruppen­niveau? | „Was sich besser darstellen lässt“; Hypothese gilt für *alle* Kohorten | Forest‑Plot (Fig 2) mit drei Hauptkohorten |
| 4 | Genotyp & CT als Haupt­variablen? | **Nicht zwingend** | Bleiben im Supplement / Text |
| 5 | Zeitliche vs. kategoriale Outcomes? | **Kategorial** | Keine Zeitachsen in Hauptfiguren |
| 6 | Missing‑Schwelle? | **Keine fixe Grenze** – Entscheidung durch Statistik | Genotyp & CT ausgelassen wegen > 50 % |
| 7 | Impfstatus wichtig? | **Randthema, irrelevant** | Impf‑Bubble‑Plots nur ggf. Supplement |
| 8 | PRISMA‑Flow nötig? | Bereits vorhanden | Kein Slotverbrauch |
| 9 | Risiko‑Bias‑Diagramm? | **Nicht benötigt** | Entfällt |
| 10 | Max. Haupt­figuren? | **Vier**; Extras ins Supplement | Fig S1 ausgelagert |

---

*Dieses Dokument bündelt sämtliche aktuellen Vorgaben, Daten­definitionen und Analysepfade. Änderungen werden versioniert gespeichert.*
