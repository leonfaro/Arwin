import pandas as pd
from data_preprocessing import TOTAL, MONO, COMBO, fill_rate

COL_ERAD = 'eradication outcome successful\n[yes / no]'
COL_SURV = 'survival outcome\n[yes / no]'
COL_AE_YN = 'any adverse events\n[yes / no]'


def flag(series, val):
    return series.astype(str).str.lower().str.startswith(val)


index = pd.Index(
    [
        'SARS-CoV-2 Persistence\u00b9, n (%)',
        'All-cause mortality\u00b2, n (%)',
        'SARS-CoV-2-related mortality\u00b3, n (%)',
        'AE\u2074, n (%)',
    ],
    name='Outcomes',
)


def build_table_B():
    tab = pd.DataFrame(index=index, columns=['Total', 'Monotherapy', 'Combination', 'p-value'])

    def add(row, ft, fm, fc):
        fill_rate(tab, row, ft, fm, fc)
    add(index[0], flag(TOTAL[COL_ERAD], 'n'), flag(MONO[COL_ERAD], 'n'), flag(COMBO[COL_ERAD], 'n'))
    add(index[1], flag(TOTAL[COL_SURV], 'n'), flag(MONO[COL_SURV], 'n'), flag(COMBO[COL_SURV], 'n'))
    add(
        index[2],
        flag(TOTAL[COL_ERAD], 'n') & flag(TOTAL[COL_SURV], 'n'),
        flag(MONO[COL_ERAD], 'n') & flag(MONO[COL_SURV], 'n'),
        flag(COMBO[COL_ERAD], 'n') & flag(COMBO[COL_SURV], 'n'),
    )
    add(index[3], flag(TOTAL[COL_AE_YN], 'y'), flag(MONO[COL_AE_YN], 'y'), flag(COMBO[COL_AE_YN], 'y'))
    tab.attrs['footnote'] = (
        'Abbreviations: AE, adverse event. n/a, not available, i.e. not reported.'
        ' NAAT, nucleic acid amplification test. NMV-r, nirmatrelvir-ritonavir.'
        ' TAC, Tacrolimus.\n'
        '1: defined as subjects with parameter \u201ceradication outcome successful: no\u201d\n'
        '2: defined as subjects with parameter \u201csurvival outcome: no\u201d\n'
        '3: defined as subjects with parameters \u201ceradication outcome successful: no\u201d'
        ' AND \u201csurvival outcome: no\u201d\n'
        '4: defined as subjects with parameter \u201cadverse events: yes\u201d'
    )
    return tab


if __name__ == '__main__':
    tab = build_table_B()
    print('Table B. Outcomes in all cohorts.')
    print(tab.to_string())
    foot = tab.attrs['footnote']
    for line in foot.split('\n'):
        if line:
            print(line)
