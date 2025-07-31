# Dataset overview

The Excel file `data_characteristics_v10.xlsx` contains three sheets:

| sheet | n |
|---|---|
| primary cohort, n=104 | 104 |
| subgroup mono n=33 | 33 |
| subgroup combo, n=57 | 57 |

# EDA for primary cohort, n=104 sheet
## first author (year)

```
Piñana
(2023): 16
Pasquini
(2023): 13
Snell
(2024): 12
Maruyama
(2024): 11
Götz
(2023): 9
Antonello
(2024): 8
Barone
(2024): 7
Breeden
(2023): 4
De Benedetto
(2024): 4
Longo
(2023): 3
Faxen
(2023): 2
Liu
(2023): 2
Almarhabi
(2024): 1
Sanmartin
(2024): 1
Sanchez
(2024): 1
Marangoni
(2023): 1
Hirotsu
(2023): 1
Lindahl
(2023): 1
Ito
(2024): 1
Gámiz
(2024): 1
Gai
(2024): 1
Ford
(2023): 1
Dentone
(2023): 1
Degtiarova
(2024): 1
Trottier
(2023): 1
```

## Baseline disease cohort  [a=autoimmunity, m=malignancy, t=transplant]

```
m: 91
a: 7
a, m: 2
t: 2
a, t: 1
t, a: 1
```

## study specific case/patient ID number

```
NA: 8
1: 8
3: 6
2: 3
6: 3
#10: 3
8: 3
4: 3
#1: 2
#8: 2
#4: 2
#2: 2
5: 2
9: 2
7: 2
UHW-001: 1
20: 1
19: 1
45: 1
239-52: 1
676-85: 1
691-8: 1
699-2: 1
958-59: 1
691-4: 1
676-49: 1
676-6: 1
676-3: 1
675-14: 1
GSTT-001: 1
OLOL-001: 1
BMT-002: 1
UHW-003: 1
676-76: 1
UHW-002: 1
BMT-001: 1
GSTT-005: 1
GSTT-004: 1
GSTT-003: 1
GSTT-002: 1
676-88: 1
#6: 1
676-75: 1
#14: 1
FR_1: 1
FR_2: 1
FR_3: 1
FR_4: 1
FR_5: 1
FR_6: 1
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
#7: 1
#9: 1
#11: 1
#12: 1
GSTT-006: 1
```

## sex [male, female]

```
m: 66
f: 35
NA: 3
```

## age

```
71: 6
66: 6
63: 5
72: 5
80: 4
58: 4
73: 4
61: 4
76: 4
55: 4
68: 3
77: 3
46: 3
78: 3
48: 3
60: 3
65: 3
81: 3
59: 3
54: 3
70: 3
64: 2
69: 2
67: 2
57: 2
79: 2
43: 1
34: 1
82: 1
35: 1
84: 1
40: 1
25: 1
56: 1
89: 1
29: 1
38: 1
39: 1
50: 1
85: 1
74: 1
```

## baseline disease

```
FL: 30
DLBCL: 13
NOS: 11
NHL: 7
CLL: 6
B-ALL: 5
MCL: 5
AML: 3
MM: 3
CLL, FL: 2
MALT: 2
LPL: 2
RA: 1
SSC, LT: 1
PCL: 1
MS: 1
KT, CU: 1
NMDA-encephalitis: 1
CREST: 1
LT: 1
ANCA-Vasculitis: 1
KT: 1
MCTD: 1
MS, DLBCL: 1
MCD: 1
MM, B-ALL: 1
NOS, RA: 1
```

## baseline therapy cohort

```
CD20: 77
Other: 13
none: 6
HSCT: 3
CAR-T: 3
HSCT, CD20: 1
CD20, CAR-T: 1
```

## Vaccination  [yes / no] (doses)

```
y (3): 29
y (2): 28
y (4): 25
y (5): 10
n: 9
y (6): 2
y (8): 1
```

## Hospitalization [yes / no]

```
y: 55
n: 49
```

## SARS-CoV-2 genotype

```
NA: 53
BA.1.1: 6
BA.5.2.1: 4
BQ.1.1: 4
BA.2: 4
BA.5.1: 3
BF.7: 2
BA.5.2.23: 2
BA.2.3: 2
XAY.1.1: 1
BA.5.2.47: 1
BA.1: 1
BA.2.9: 1
BQ.1.1.3: 1
BQ.1.1.2 : 1
EG.5.1.6: 1
XBB.1.16.1: 1
FR.1: 1
BA.5.2.20: 1
BA.1.1.1: 1
BA.1.1.2: 1
BF.1: 1
BA5.6: 1
BF.7.14: 1
CH.1.1: 1
BF.28: 1
JG.3: 1
HH.1: 1
XBF: 1
BQ.1.5: 1
XCH.1: 1
EG.5.1: 1
BQ.1.1.8: 1
```

## CT lung changes? [yes / no]

```
y: 62
n: 42
```

## SARS-CoV-2 replication [days]

```
NA: 7
21: 4
33: 3
61: 3
76: 3
91: 2
46: 2
25: 2
152: 2
35: 2
29: 2
31: 2
13: 2
42: 2
104: 2
62: 2
64: 2
9: 2
27: 2
43: 1
45: 1
144: 1
57: 1
48: 1
116: 1
30: 1
94: 1
92: 1
137: 1
135: 1
53: 1
4: 1
236: 1
7: 1
40: 1
138: 1
155: 1
134: 1
215: 1
72: 1
103: 1
203: 1
101: 1
167: 1
160: 1
41: 1
98: 1
218: 1
26: 1
20: 1
102: 1
169: 1
38: 1
272: 1
24: 1
78: 1
11: 1
244: 1
36: 1
183: 1
242: 1
122: 1
14: 1
44: 1
213: 1
73: 1
216: 1
79: 1
130: 1
156: 1
96: 1
71: 1
93: 1
69: 1
120: 1
```

## any glucocorticosteroid usage [yes / no]

```
n: 57
y: 47
```

## 1st line treatment any other antiviral drugs  (days) [dosage]

```
none: 49
RDV (5): 8
TIX-CIL [1]: 4
RDV (10): 3
SOT [1]: 3
SOT [1] → CAS-IMD [1] → RDV (7): 2
RDV (10) → TIX-CIL [1]: 2
MPV (5): 2
BEB [1]: 2
BEB [1] → RDV (10): 1
CAS-IMD [1]: 1
MPV (5) → RDV (10) → SOT [1] → RDV (21) → SOT [1] → IVIg: 1
RDV (10) → RDV (5) → SOT [1]: 1
RDV (25) → SOT [1]: 1
RDV (5) → RDV (5): 1
RDV (5) → TIX-CIL [1] → RDV (5) → RDV (5) → covalescent plasma [1]: 1
MPV (5 days): 1
SOT [1] → TIX-CIL [1] → RDV (5): 1
SOT [1] → ENS (10): 1
SOT [1] → CAS-IMD [1] → TIX-CIL [1] → MPV (10) → ENS (5) → RDV (5) → ENS (10): 1
CAS-IMD [1] → TIX-CIL [1] → RDV (10) → ENS (10): 1
CAS-IMD [1] → TIX-CIL [1] → RDV (30): 1
CAS-IMD [1] → MPV (5) → RDV (8): 1
CAS-IMD [1] → MPV (10): 1
TIX-CIL [2] → RDV (7) → RDV (7) → BEB [1]: 1
CAS-IMD [1] → RDV (4): 1
MPV (5) → SOT [1]: 1
RDV (7): 1
MPV (15) → SOT [1]: 1
TIX-CIL [1] → RDV (4): 1
RDV (25) → MPV (n/a) → TIX-CIL [n/a]: 1
SOT [6] → RDV (35) [4] → MPV [4] → IVIg [7]: 1
MPV (5) + RDV (5) + RDV (5) + RDV (10): 1
MPV (38): 1
MPV (n/a) → TIX-CIL (n/a): 1
CAS-IMD [1] → SOT [1] → RDV (10): 1
TIX-CIL [3] → RDV (5): 1
RDV (10) → BEB [1]: 1
```

## 1st line standard Paxlovid treatment [yes / no]

```
n: 74
y: 30
```

## 1st line Paxlovid standard duration treatment courses  (n)

```
0: 73
1: 29
2: 1
3: 1
```

## 2nd line treatment form of therapy  [m / c] mono: only Paxlovid combination: Paxlovid + any other antiviral drugs

```
c: 63
m: 41
```

## 2nd line extended Paxlovid treatment  total days [courses]

```
10 [1]: 58
15 [1]: 9
6 [1]: 3
14 [1]: 3
8 [1]: 3
21 [1]: 3
20 [1]: 3
20 [2]: 3
7 [1]: 3
18 [1]: 3
9 [1]: 2
13 [1]: 2
35 [1]: 1
22 [1]: 1
36 [2]: 1
24 [1]: 1
19 [2]: 1
5 [1]: 1
34 [1]: 1
61 [1]: 1
12 [1]: 1
```

## 2nd line any other concomitant antiviral therapy  (days)  [dosages]

```
none: 36
RDV (10): 20
MPV (10): 7
IvIg: 3
RDV (5): 3
RDV (1): 3
SOT [1]: 3
RDV [10]: 2
MPV (15): 2
RDV (8): 2
RDV 10 (1): 2
RDV (10) + SOT [1]: 2
TIX-CIL [1] → RDV (10) → RDV (10) → MPV (10): 1
TIX-CIL [2]: 1
RDV (1) + SOT [1]: 1
RDV (12): 1
RDV (22): 1
RDV (13): 1
RDV (10) + MPV (10): 1
RDV (14): 1
SOT [6]: 1
MPV 5 (directly afterwards): 1
MPV 34 (1): 1
MPV 28 (1) + RDV 21 (1): 1
MPV 39 (1): 1
RDV 5 (1): 1
RDV 7 (1): 1
RDV (9): 1
TIX-CIL [1]: 1
MPV (8): 1
RDV (20): 1
```

## eradication outcome successful [yes / no]

```
y: 90
n: 11
NA: 3
```

## survival outcome [yes / no]

```
y: 94
n: 10
```

## any adverse events [yes / no]

```
n: 98
y: 6
```

## type of adverse event

```
none: 68
n: 30
nausea, dysgeusia: 1
dysgeusia: 1
abdominal bloating: 1
Supratherapeutic TAC: 1
acute acalculous cholecystitis: 1
thrombocytopenia: 1
```

