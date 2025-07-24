# EDA for primary cohort, clean sheet
## first author (year)

- **dtype:** object
- **missing:** 57
- **unique values:** 25

```
NA: 57
Piñana (2023): 16
Pasquini (2023): 13
Snell (2024): 12
Maruyama (2024): 11
Götz (2023): 9
Antonello (2024): 8
Barone (2024): 7
De Benedetto (2024): 4
Breeden (2023): 4
Longo (2023): 3
Faxen (2023): 2
Liu (2023): 2
Gai (2024): 1
Almarhabi (2024): 1
Ford (2023): 1
Dentone (2023): 1
Degtiarova (2024): 1
Marangoni (2023): 1
Lindahl (2023): 1
Hirotsu (2023): 1
Ito (2024): 1
Gámiz (2024): 1
Sanchez (2024): 1
Sanmartin (2024): 1
Trottier (2023): 1
```

## Baseline disease cohort  [a=autoimmunity, m=malignancy, t=transplant]

- **dtype:** object
- **missing:** 57
- **unique values:** 6

```
m: 92
NA: 57
a: 6
a, m: 2
t: 2
a, t: 1
t, a: 1
```

## study specific case/patient ID number

- **dtype:** object
- **missing:** 65
- **unique values:** 67

```
NA: 65
1: 8
3: 6
2: 3
#10: 3
8: 3
6: 3
4: 3
#1: 2
5: 2
7: 2
#2: 2
9: 2
#4: 2
#8: 2
FR_2: 1
GSTT-006: 1
GSTT-004: 1
GSTT-003: 1
GSTT-002: 1
GSTT-001: 1
FR_1: 1
676-6: 1
20: 1
675-14: 1
676-3: 1
FR_7: 1
FR_8: 1
FR_9: 1
12: 1
13: 1
17: 1
18: 1
26: 1
33: 1
38: 1
43: 1
#3: 1
#5: 1
#6: 1
#7: 1
#9: 1
#11: 1
#12: 1
#14: 1
676-75: 1
676-76: 1
676-88: 1
19: 1
45: 1
239-52: 1
676-85: 1
691-8: 1
UHW-001: 1
UHW-002: 1
UHW-003: 1
FR_3: 1
FR_4: 1
FR_5: 1
FR_6: 1
699-2: 1
958-59: 1
691-4: 1
676-49: 1
OLOL-001: 1
BMT-002: 1
BMT-001: 1
GSTT-005: 1
```

## sex [male, female]

- **dtype:** object
- **missing:** 60
- **unique values:** 2

```
m: 66
NA: 60
f: 35
```

## age

- **dtype:** float64
- **missing:** 57
- **unique values:** 41
- **range:** 25.0 to 89.0

```
NA: 57
71.0: 6
66.0: 6
63.0: 5
72.0: 5
73.0: 4
61.0: 4
58.0: 4
76.0: 4
55.0: 4
80.0: 4
48.0: 3
68.0: 3
46.0: 3
65.0: 3
60.0: 3
81.0: 3
78.0: 3
59.0: 3
77.0: 3
54.0: 3
70.0: 3
69.0: 2
79.0: 2
67.0: 2
57.0: 2
64.0: 2
85.0: 1
40.0: 1
25.0: 1
82.0: 1
43.0: 1
84.0: 1
34.0: 1
89.0: 1
56.0: 1
35.0: 1
29.0: 1
39.0: 1
38.0: 1
50.0: 1
74.0: 1
```

## baseline disease

- **dtype:** object
- **missing:** 57
- **unique values:** 34

```
NA: 57
FL: 28
DLBCL: 12
Haematological malignancy: 8
NHL: 6
CLL: 6
B-ALL: 5
MCL: 4
MM: 3
AML: 3
CLL, FL: 2
LPL: 2
MALT: 2
Follicular lymphoma: 2
MS, DLBCL: 1
MCD: 1
MM, B-ALL: 1
MCTD: 1
DLBCL in HIV/AIDS: 1
Lung-TX: 1
ANCA-associated Glomerulonephritis + IgA Nephropathy: 1
Kidney-TX: 1
CREST: 1
Kidney-TX + Colitis ulcerosa: 1
Mantle cell lymphoma: 1
Systemic sclerosis + Lung-TX: 1
Plasma cell maturing marginal zone B-cell lymphoma of the skin: 1
MS: 1
Indolent NHL: 1
Malignant Lymphoma: 1
Plasma cell leukemia (PCL): 1
NMDA-receptor encephalitis: 1
Hematological malignancy : 1
Rheumatoid arthritis: 1
Haematological malignancy, Rheumatoid arthritis: 1
```

## baseline therapy cohort

- **dtype:** object
- **missing:** 57
- **unique values:** 7

```
CD20: 77
NA: 57
Other: 13
none: 6
HSCT: 3
CAR-T: 3
HSCT, CD20: 1
CD20, CAR-T: 1
```

## Vaccination  [yes / no] (doses)

- **dtype:** object
- **missing:** 2
- **unique values:** 61

```
y (3): 29
y (2): 28
y (4): 25
y (5): 10
n: 9
y (6): 2
NA: 2
MS: 2
Abbrevation: 1
y (8): 1
ASCT: 1
BEB: 1
BEN: 1
AML: 1
CAR-T: 1
CAS-IMD: 1
CLL: 1
CVAD: 1
CVID: 1
CYC: 1
DHAP: 1
DRC: 1
DXA: 1
ENS: 1
FCR: 1
FL: 1
GB: 1
GEMOX: 1
Gm: 1
BFM: 1
GPA: 1
IBR: 1
LPL: 1
IvIg: 1
MCD: 1
MCL: 1
MCTD: 1
MALT: 1
MGUS: 1
Mini-Hyper-CVD: 1
MMF: 1
MM: 1
MPN: 1
MPV: 1
NHL: 1
NMV-r: 1
OBI: 1
PDN: 1
Pola-BR: 1
POMP: 1
RB: 1
R-CHOP: 1
R-COMP: 1
R-DHAP: 1
RDV: 1
R-GEMOX: 1
Rm: 1
R-MAGRATH: 1
RTX: 1
SCIG: 1
SOT: 1
TIX-CIL: 1
```

## Hospitalization [yes / no]

- **dtype:** object
- **missing:** 1
- **unique values:** 57

```
y: 55
n: 49
Multiple sclerosis: 2
NA: 1
Acute myeloid leukaemia: 1
Full Form: 1
Bebtelovimab: 1
Bendamustine: 1
Berlin‐Frankfurt‐Munich: 1
Autologous stem cell transplant: 1
Casivirimab-imdevimab: 1
Chronic lymphocytic leukaemia: 1
Cyclophosphamide, vincristine, doxorubicin, dexamethasone: 1
Common variable immunodeficiency: 1
Cyclophosphamide: 1
Dexamethasone, high‐dose Ara‐C ‐ cytarabine, platinol: 1
Dexamethasone+rituximab+cyclophosphamide: 1
Dexamethasone: 1
Ensitrelvir: 1
Fludarabine + ciclofosfamide + rituximab: 1
Follicular lymphoma: 1
Obinutuzumab+bendamustine: 1
Gemcitabine + oxaliplatin: 1
Obinutuzumab maintenance: 1
Granulomatosis with polyangiitis: 1
Chimeric antigen receptor T cell therapy: 1
Ibrutinib: 1
intravenous Immunglobulins: 1
Mucosa-associated lymphoid tissue: 1
Lymphoplasmacytic lymphoma: 1
Mantle cell lymphoma: 1
mixed connective tissue disease: 1
Monoclonal gаmmорathу of undetermined significance : 1
Minimal change disease glomerulonephritis: 1
Cyclophosphamide + dexamethasone + methotrexate + cytarabine: 1
Multiple myeloma: 1
Methyprednisolone: 1
Mycophenolate mofetil: 1
Molnupiravir: 1
not available : 1
Non-Hodgkin Lymphoma: 1
Nirmatrelvir-ritonavir: 1
Obinutuzumab: 1
Prednisone: 1
Polatuzumab vedotin+bendamustine+rituximab: 1
Prednisone + vincristine + methotrexate + 6-mercaptopurine: 1
Rituximab+bendamustine: 1
rituximab+cyclophosphamide+doxorubicin+vincristine+prednisolone: 1
Prednisone + cyclophosphamide + vincristine + non-pegylated liposomal doxorubicin (MyocetTM) and rituximab: 1
Rituximab+dexamethasone+cytarabine+cisplatin: 1
Remdesivir: 1
Rituximab + gemcitabine + oxaliplatin: 1
Rituximab maintenance: 1
Rituximab + cyclophosphamide + vincristine + doxorubicin-methotrexate + ifosfamide + etoposide + cytarabine: 1
Rituximab: 1
subcutaneous immunoglobins: 1
Sotrovimab: 1
Tixagevimab-cilgavimab: 1
```

## SARS-CoV-2 genotype

- **dtype:** object
- **missing:** 110
- **unique values:** 32

```
NA: 110
BA.1.1: 6
BA.5.2.1: 4
BQ.1.1: 4
BA.2: 4
BA.5.1: 3
BF.7: 2
BA.2.3: 2
BA.5.2.23: 2
XCH.1: 1
EG.5.1: 1
BF.1: 1
XBF: 1
JG.3: 1
HH.1: 1
XAY.1.1: 1
BQ.1.5: 1
CH.1.1: 1
BF.28: 1
BF.7.14: 1
BA5.6: 1
BA.5.2.47: 1
BA.1.1.2: 1
BA.1.1.1: 1
BA.5.2.20: 1
FR.1: 1
XBB.1.16.1: 1
EG.5.1.6: 1
BQ.1.1.2 : 1
BQ.1.1.3: 1
BA.2.9: 1
BA.1: 1
BQ.1.1.8: 1
```

## CT lung changes? [yes / no]

- **dtype:** object
- **missing:** 57
- **unique values:** 2

```
y: 62
NA: 57
n: 42
```

## SARS-CoV-2 replication [days]

- **dtype:** float64
- **missing:** 64
- **unique values:** 74
- **range:** 4.0 to 272.0

```
NA: 64
21.0: 4
33.0: 3
61.0: 3
76.0: 3
27.0: 2
62.0: 2
9.0: 2
42.0: 2
35.0: 2
46.0: 2
104.0: 2
152.0: 2
13.0: 2
91.0: 2
31.0: 2
29.0: 2
64.0: 2
25.0: 2
167.0: 1
4.0: 1
135.0: 1
7.0: 1
155.0: 1
215.0: 1
94.0: 1
218.0: 1
26.0: 1
20.0: 1
102.0: 1
169.0: 1
38.0: 1
272.0: 1
36.0: 1
183.0: 1
242.0: 1
122.0: 1
14.0: 1
44.0: 1
213.0: 1
73.0: 1
216.0: 1
79.0: 1
130.0: 1
156.0: 1
160.0: 1
96.0: 1
71.0: 1
93.0: 1
69.0: 1
98.0: 1
41.0: 1
40.0: 1
92.0: 1
57.0: 1
144.0: 1
45.0: 1
43.0: 1
48.0: 1
116.0: 1
30.0: 1
72.0: 1
103.0: 1
78.0: 1
11.0: 1
244.0: 1
53.0: 1
203.0: 1
101.0: 1
236.0: 1
137.0: 1
134.0: 1
138.0: 1
24.0: 1
120.0: 1
```

## any glucocorticosteroid usage [yes / no]

- **dtype:** object
- **missing:** 57
- **unique values:** 2

```
n: 57
NA: 57
y: 47
```

## 1st line treatment any other antiviral drugs  (days) [dosage]

- **dtype:** object
- **missing:** 57
- **unique values:** 38

```
NA: 57
none: 49
RDV (5): 8
TIX-CIL [1]: 4
SOT [1]: 3
RDV (10): 3
MPV (5): 2
SOT [1] → CAS-IMD [1] → RDV (7): 2
BEB [1]: 2
RDV (10) → TIX-CIL [1]: 2
MPV (5) → SOT [1]: 1
MPV (38): 1
MPV (15) → SOT [1]: 1
RDV (7): 1
TIX-CIL [2] → RDV (7) → RDV (7) → BEB [1]: 1
TIX-CIL [3] → RDV (5): 1
CAS-IMD [1] → SOT [1] → RDV (10): 1
BEB [1] → RDV (10): 1
MPV (5) + RDV (5) + RDV (5) + RDV (10): 1
TIX-CIL [1] → RDV (4): 1
RDV (25) → MPV (n/a) → TIX-CIL [n/a]: 1
SOT [6] → RDV (35) [4] → MPV [4] → IVIg [7]: 1
MPV (n/a) → TIX-CIL (n/a): 1
CAS-IMD [1] → RDV (4): 1
CAS-IMD [1] → MPV (10): 1
CAS-IMD [1] → MPV (5) → RDV (8): 1
CAS-IMD [1]: 1
CAS-IMD [1] → TIX-CIL [1] → RDV (10) → ENS (10): 1
SOT [1] → CAS-IMD [1] → TIX-CIL [1] → MPV (10) → ENS (5) → RDV (5) → ENS (10): 1
SOT [1] → ENS (10): 1
CAS-IMD [1] → TIX-CIL [1] → RDV (30): 1
SOT [1] → TIX-CIL [1] → RDV (5): 1
MPV (5 days): 1
RDV (5) → RDV (5): 1
RDV (5) → TIX-CIL [1] → RDV (5) → RDV (5) → covalescent plasma [1]: 1
RDV (25) → SOT [1]: 1
RDV (10) → RDV (5) → SOT [1]: 1
MPV (5) → RDV (10) → SOT [1] → RDV (21) → SOT [1] → IVIg: 1
RDV (10) → BEB [1]: 1
```

## 1st line standard Paxlovid treatment [yes / no]

- **dtype:** object
- **missing:** 57
- **unique values:** 2

```
n: 74
NA: 57
y: 30
```

## 1st line Paxlovid standard duration treatment courses  (n)

- **dtype:** float64
- **missing:** 57
- **unique values:** 4
- **range:** 0.0 to 3.0

```
0.0: 73
NA: 57
1.0: 29
2.0: 1
3.0: 1
```

## 2nd line treatment form of therapy  [m / c] mono: only Paxlovid combination: Paxlovid + any other antiviral drugs

- **dtype:** object
- **missing:** 57
- **unique values:** 2

```
c: 63
NA: 57
m: 41
```

## 2nd line extended Paxlovid treatment  total days [courses]

- **dtype:** object
- **missing:** 57
- **unique values:** 21

```
10 [1]: 58
NA: 57
15 [1]: 9
14 [1]: 3
6 [1]: 3
7 [1]: 3
18 [1]: 3
8 [1]: 3
20 [1]: 3
21 [1]: 3
20 [2]: 3
9 [1]: 2
13 [1]: 2
24 [1]: 1
5 [1]: 1
34 [1]: 1
61 [1]: 1
19 [2]: 1
36 [2]: 1
35 [1]: 1
22 [1]: 1
12 [1]: 1
```

## 2nd line any other concomitant antiviral therapy  (days)  [dosages]

- **dtype:** object
- **missing:** 57
- **unique values:** 31

```
NA: 57
none: 36
RDV (10): 20
MPV (10): 7
IvIg: 3
SOT [1]: 3
RDV (1): 3
RDV (5): 3
RDV 10 (1): 2
MPV (15): 2
RDV (8): 2
RDV (10) + SOT [1]: 2
RDV [10]: 2
RDV (9): 1
RDV (10) + MPV (10): 1
RDV (14): 1
TIX-CIL [1]: 1
TIX-CIL [2]: 1
MPV (8): 1
TIX-CIL [1] → RDV (10) → RDV (10) → MPV (10): 1
MPV 28 (1) + RDV 21 (1): 1
RDV 7 (1): 1
MPV 39 (1): 1
RDV 5 (1): 1
SOT [6]: 1
MPV 5 (directly afterwards): 1
MPV 34 (1): 1
RDV (13): 1
RDV (22): 1
RDV (12): 1
RDV (1) + SOT [1]: 1
RDV (20): 1
```

## eradication outcome successful [yes / no]

- **dtype:** object
- **missing:** 60
- **unique values:** 2

```
y: 90
NA: 60
n: 11
```

## survival outcome [yes / no]

- **dtype:** object
- **missing:** 57
- **unique values:** 2

```
y: 94
NA: 57
n: 10
```

## any adverse events [yes / no]

- **dtype:** object
- **missing:** 57
- **unique values:** 2

```
n: 98
NA: 57
y: 6
```

## type of adverse event

- **dtype:** object
- **missing:** 57
- **unique values:** 8

```
none: 68
NA: 57
n: 30
dysgeusia: 1
nausea, dysgeusia: 1
abdominal bloating: 1
Supratherapeutic TAC: 1
acute acalculous cholecystitis: 1
thrombocytopenia: 1
```
