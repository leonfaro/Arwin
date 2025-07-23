import pandas as pd
import numpy as np
import re
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu, shapiro, ttest_ind
FILE_PATH = 'data characteristics v7, clean.xlsx'
COL_OTHER = '1st line treatment any other antiviral drugs \n(days) [dosage]'
COL_NMV_STD = '1st line Paxlovid standard duration treatment courses \n(n)'
COL_THERAPY = (
    '2nd line treatment form of therapy \n[m / c]\nmono: only Paxlovid\n'
    'combination: Paxlovid + any other antiviral drugs'
)
COL_EXT = '2nd line extended Paxlovid treatment \n(total days) [courses]'
COL_SEX = 'sex\n[male, female]'
COL_AGE = 'age'
COL_DIS = 'Baseline disease cohort \n[a=autoimmunity, m=malignancy, t=transplant]'
COL_BASE = 'Baseline therapy cohort'
COL_GC = 'any glucocorticosteroid usage\n[yes / no]'
COL_VACC = 'Vaccination \n[yes / no] (doses)'
COL_CT = 'CT lung changes?\n[yes / no]'
COL_HOSP = 'Hospitalization\n[yes / no]'


def load_sheet(primary, alt):
    try:
        return pd.read_excel(FILE_PATH, sheet_name=primary)
    except ValueError:
        return pd.read_excel(FILE_PATH, sheet_name=alt)


TOTAL = load_sheet('primary cohort, clean', 'primary cohort, n=104')
MONO = load_sheet('subgroup mono', 'subgroup mono n=33')
COMBO = load_sheet('subgroup combo', 'subgroup combo, n=57')
for _df in (TOTAL, MONO, COMBO):
    s = _df[COL_OTHER].astype(str).str.lower()
    _df['flag_pax5d'] = pd.to_numeric(_df[COL_NMV_STD], errors='coerce').fillna(0) > 0
    _df['flag_rdv'] = s.str.contains('rdv') | s.str.contains('remdesivir')
    _df['flag_mpv'] = s.str.contains('mpv') | s.str.contains('molnupiravir')
    nn = s.str.strip().ne('none') & s.str.contains('[a-z]', na=False)
    _df['flag_other'] = nn & ~(_df['flag_rdv'] | _df['flag_mpv'])
DF_mono = MONO.copy()
DF_comb = COMBO.copy()


def parse_ext(series: pd.Series):
    pattern = r'(\d+(?:\.\d+)?)\s*(?:\(|\[)?(\d+)(?:\)|\])?'
    tmp = series.astype(str).str.extract(pattern)
    days = tmp[0].astype(float)
    courses = tmp[1].astype(float)
    return days, courses


def chi_or_fisher(a11, a12, a21, a22):
    try:
        exp = chi2_contingency([[a11, a12], [a21, a22]])[3]
    except ValueError:
        return fisher_exact([[a11, a12], [a21, a22]])[1]
    if (exp < 5).any():
        return fisher_exact([[a11, a12], [a21, a22]])[1]
    return chi2_contingency([[a11, a12], [a21, a22]])[1]


def cont_test(v1, v2):
    if shapiro(v1).pvalue >= 0.05 and shapiro(v2).pvalue >= 0.05:
        return ttest_ind(v1, v2, equal_var=False).pvalue
    return mannwhitneyu(v1, v2).pvalue


def parse_vacc(x: str):
    s = str(x).lower()
    m = pd.Series(s).str.extract(r'(\d+)')[0]
    dose = float(m.iloc[0]) if m.notna().any() else np.nan
    if s.startswith('y'):
        return 'Yes', dose
    if s.startswith('n'):
        return 'No', dose
    return 'Unknown', dose


def group_immuno(x: str) -> str:
    tags = re.split(r'[,\s]+', str(x).lower())
    labs = set()
    for t in tags:
        if not t:
            continue
        if 'cd20' in t:
            labs.add('CD20')
        elif 'car' in t:
            labs.add('CAR-T')
        elif 'hsct' in t:
            labs.add('HSCT')
        elif 'none' in t:
            labs.add('none')
        else:
            labs.add('Other')
    if not labs:
        return 'none'
    return labs.pop() if len(labs) == 1 else 'Mixed'


def fmt_p(p):
    if p < 0.001:
        return '<0.001'
    return f'{round(p, 3):.3f}'


def fmt_pct(n: int, d: int) -> str:
    return f'{n} ({n / d * 100:.1f}%)' if d else '0 (0.0%)'


def fmt_iqr(series: pd.Series) -> str:
    return f'{int(series.median())} ({int(series.quantile(0.25))}-{int(series.quantile(0.75))})'


def fmt_range(series: pd.Series) -> str:
    return f'{int(series.min())}-{int(series.max())}'


def baseline_stats() -> pd.DataFrame:
    labels = ['CD20', 'CAR-T', 'HSCT', 'Other', 'none', 'Mixed']
    t = TOTAL[COL_BASE].map(group_immuno)
    m = MONO[COL_BASE].map(group_immuno)
    c = COMBO[COL_BASE].map(group_immuno)
    df = pd.DataFrame(index=labels, columns=[
        'Total n',
        'Total %',
        'Mono n',
        'Mono %',
        'Combo n',
        'Combo %',
        'p-value',
    ])
    for lab in labels:
        a11 = int((c == lab).sum())
        a12 = len(c) - a11
        a21 = int((m == lab).sum())
        a22 = len(m) - a21
        p = chi_or_fisher(a11, a12, a21, a22)
        df.loc[lab] = [
            int((t == lab).sum()),
            (t == lab).mean() * 100,
            a21,
            (m == lab).mean() * 100,
            a11,
            (c == lab).mean() * 100,
            fmt_p(p),
        ]
    return df


if __name__ == '__main__':
    print(TOTAL.shape)
    print(MONO.shape)
    print(COMBO.shape)
    print(baseline_stats())
