import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu, shapiro, ttest_ind
COL_OTHER = '1st line treatment any other antiviral drugs \n(days) [dosage]'
COL_NMV_STD = '1st line NMV-r standard duration treatment courses \n(n)'
COL_THERAPY = (
    '2nd line treatment form of therapy \n[m / c]\nmono: only NMV-r\n'
    'combination: NMV-r + any other antiviral drugs'
)
COL_EXT = '2nd line extended NMV-r treatment \n(total days) [courses]'
COL_SEX = 'sex\n[male, female]'
COL_AGE = 'age'
COL_DIS = 'Baseline disease cohort \n[a=autoimmunity, m=malignancy, t=transplant]'
COL_BASE = 'baseline therapy'
COL_GC = 'any glucocorticosteroid usage\n[yes / no]'
COL_VACC = 'Vaccination \n[yes / no] (doses)'
COL_CT = 'CT lung changes?\n[yes / no]'
COL_HOSP = 'Hospitalization\n[yes / no]'

TOTAL = pd.read_excel('Total.xlsx')
MONO = pd.read_excel('Monotherapy.xlsx')
COMBO = pd.read_excel('Combination.xlsx')
DF_mono = pd.read_excel('Monotherapy.xlsx')
DF_comb = pd.read_excel('Combination.xlsx')


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
    s = str(x).lower()
    if any(k in s for k in ('ritux', 'obinu', 'ocrel', 'mosune', 'cd-20')):
        return 'Anti-CD20'
    if 'car' in s:
        return 'CAR-T'
    if 'hsct' in s or 'asct' in s:
        return 'HSCT'
    if 'none' in s or 'no is' in s or not s:
        return 'None'
    return 'Other'


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
