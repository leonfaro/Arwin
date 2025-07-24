import pandas as pd
import numpy as np
import re
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu, shapiro, ttest_ind
FILE_PATH = 'data characteristics v10.xlsx'
COL_OTHER = '1st line treatment any other antiviral drugs \n(days) [dosage]'
COL_NMV_STD = '1st line Paxlovid standard duration treatment courses \n(n)'
COL_THERAPY = (
    '2nd line treatment form of therapy \n[m / c]\nmono: only Paxlovid\n'
    'combination: Paxlovid + any other antiviral drugs'
)
COL_EXT = '2nd line extended Paxlovid treatment \ntotal days [courses]'
COL_SEX = 'sex\n[male, female]'
COL_AGE = 'age'
COL_DIS = 'Baseline disease cohort \n[a=autoimmunity, m=malignancy, t=transplant]'
COL_BASE = 'Baseline therapy cohort'
COL_GC = 'any glucocorticosteroid usage\n[yes / no]'
COL_VACC = 'Vaccination \n[yes / no] (doses)'
COL_CT = 'CT lung changes?\n[yes / no]'
COL_HOSP = 'Hospitalization\n[yes / no]'
COL_REP = 'SARS-CoV-2 replication\n[days]'
COL_GENO = 'SARS-CoV-2 genotype'
COL_SURV = 'survival outcome\n[yes / no]'
COL_AE_TYPE = 'type of adverse event'


def load_sheet(primary, alt):
    try:
        return pd.read_excel(FILE_PATH, sheet_name=primary)
    except ValueError:
        return pd.read_excel(FILE_PATH, sheet_name=alt)


TOTAL = load_sheet('primary cohort, clean', 'primary cohort, n=104').iloc[:104]
MONO = load_sheet('subgroup mono', 'subgroup mono n=33')
COMBO = load_sheet('subgroup combo', 'subgroup combo, n=57')
TOTAL_N = len(TOTAL)
MONO_N = len(MONO)
COMBO_N = len(COMBO)
for _df in (TOTAL, MONO, COMBO):
    if 'baseline therapy cohort' in _df.columns and COL_BASE not in _df.columns:
        _df.rename(columns={'baseline therapy cohort': COL_BASE}, inplace=True)
    for c in list(_df.columns):
        if c.startswith('2nd line extended Paxlovid treatment'):
            _df.rename(columns={c: COL_EXT}, inplace=True)
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
        chi2, p, df, exp = chi2_contingency([[a11, a12], [a21, a22]])
    except ValueError:
        return fisher_exact([[a11, a12], [a21, a22]])[1], 'Fisher'
    if (exp < 5).any():
        return fisher_exact([[a11, a12], [a21, a22]])[1], 'Fisher'
    return chi2_contingency([[a11, a12], [a21, a22]])[1], 'Chi2 df=1'


def cont_test(v1, v2):
    if shapiro(v1).pvalue >= 0.05 and shapiro(v2).pvalue >= 0.05:
        t = ttest_ind(v1, v2, equal_var=False)
        n1 = len(v1)
        n2 = len(v2)
        s1 = v1.var(ddof=1)
        s2 = v2.var(ddof=1)
        df = (s1 / n1 + s2 / n2) ** 2 / ((s1 / n1) ** 2 / (n1 - 1) + (s2 / n2) ** 2 / (n2 - 1))
        return t.pvalue, f'Welch df={df:.1f}'
    u, p = mannwhitneyu(v1, v2)
    return p, f'Mann-Whitney U={u:.1f}'


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


def heme_subtype(x):
    s = str(x).lower()
    if 'dlbcl' in s:
        return 'DLBCL'
    if 'all' in s:
        return 'ALL'
    if 'cll' in s and ',' not in s:
        return 'CLL'
    if 'aml' in s:
        return 'AML'
    if 'follicular' in s or s.strip() == 'fl' or ' fl' in s:
        return 'FL'
    if 'nhl' in s or 'lymphoma' in s or 'mcl' in s or 'lpl' in s or 'malt' in s:
        return 'NHL'
    if 'mm' in s or 'pcl' in s or 'myeloma' in s:
        return 'MM'
    if ',' in s or '+' in s:
        return 'Mixed'
    if s.strip():
        return 'Other'
    return None


def auto_subtype(x):
    s = str(x).lower()
    if 'mctd' in s:
        return 'MCTD'
    if 'rheumatoid' in s or s.strip() == 'ra':
        return 'RA'
    if 'crest' in s:
        return 'CREST'
    if 'ms' in s and 'mcl' not in s:
        return 'MS'
    if 'systemic sclerosis' in s:
        return 'Systemic sclerosis'
    if 'ulcerosa' in s:
        return 'Colitis ulcerosa'
    if 'glomerulonephritis' in s:
        return 'Glomerulonephritis'
    if 'nmda' in s:
        return 'NMDA-receptor encephalitis'
    return None


def transp_subtype(x):
    s = str(x).lower()
    if 'lung' in s and 'tx' in s:
        return 'Lung-TX'
    if 'kidney' in s and 'tx' in s:
        return 'Kidney-TX'
    return None


def disease_group(x):
    s = str(x).lower()
    if 'm' in s:
        return 'Haematological malignancy'
    if 't' in s:
        return 'Transplantation'
    if 'a' in s:
        return 'Autoimmune disease'
    return None


def immuno_cat(x):
    g = group_immuno(x)
    if g == 'CD20':
        return 'Anti-CD-20'
    if g == 'CAR-T':
        return 'CAR-T'
    if g == 'none':
        return 'None'
    return 'None'


def geno_cat(x):
    s = str(x).lower()
    if (
        s.startswith('ba.5')
        or s.startswith('ba5')
        or s.startswith('bf')
        or s.startswith('bq')
        or s.startswith('be')
        or s.startswith('ch')
        or s.startswith('eg')
        or s.startswith('fr')
        or s.startswith('jg')
        or s.startswith('hh')
    ):
        return 'BA.5-derived Omicron subvariant'
    if 'ba.2' in s or s.startswith(('ba2', 'xd', 'xay')):
        return 'BA.2-derived Omicron subvariant'
    if 'ba.1' in s or s.startswith('ba1'):
        return 'BA.1-derived Omicron subvariant'
    if s:
        return 'Other'
    return None


def ae_cat(x):
    s = str(x).lower()
    if 'thrombocytopenia' in s:
        return 'Thrombocytopenia'
    if not s or s in {'none', 'n', 'nan'}:
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


def rate_calc(ft, fm, fc):
    nt = int(ft.sum())
    nm = int(fm.sum())
    nc = int(fc.sum())
    p, test = chi_or_fisher(nc, len(fc) - nc, nm, len(fm) - nm)
    return nt, nm, nc, p, test


def vec_calc(vt, vm, vc):
    vt = pd.to_numeric(vt, errors='coerce').dropna()
    vm = pd.to_numeric(vm, errors='coerce').dropna()
    vc = pd.to_numeric(vc, errors='coerce').dropna()
    p, test = cont_test(vm, vc)
    return vt, vm, vc, p, test


def fill_rate(tab, row, ft, fm, fc, blank=False):
    nt, nm, nc, p, test = rate_calc(ft, fm, fc)
    tab.at[row, 'Total'] = fmt_pct(nt, TOTAL_N)
    tab.at[row, 'Monotherapy'] = fmt_pct(nm, MONO_N)
    tab.at[row, 'Combination'] = fmt_pct(nc, COMBO_N)
    tab.at[row, 'p-value'] = '' if blank and nt == 0 else fmt_p(p)
    tab.at[row, 'Test'] = '' if blank and nt == 0 else test
    return nt, nm, nc, p, test


def fill_median_iqr(tab, row, vt, vm, vc):
    vt, vm, vc, p, test = vec_calc(vt, vm, vc)
    tab.at[row, 'Total'] = fmt_iqr(vt)
    tab.at[row, 'Monotherapy'] = fmt_iqr(vm)
    tab.at[row, 'Combination'] = fmt_iqr(vc)
    tab.at[row, 'p-value'] = fmt_p(p)
    tab.at[row, 'Test'] = test
    return vt, vm, vc, p, test


def fill_mean_range(tab, row, vt, vm, vc):
    vt, vm, vc, p, test = vec_calc(vt, vm, vc)
    tab.at[row, 'Total'] = f'{vt.mean():.1f} ({fmt_range(vt)})'
    tab.at[row, 'Monotherapy'] = f'{vm.mean():.1f} ({fmt_range(vm)})'
    tab.at[row, 'Combination'] = f'{vc.mean():.1f} ({fmt_range(vc)})'
    tab.at[row, 'p-value'] = fmt_p(p)
    tab.at[row, 'Test'] = test
    return vt, vm, vc, p, test


def fill_range(tab, row, vt, vm, vc):
    vt, vm, vc, p, test = vec_calc(vt, vm, vc)
    tab.at[row, 'Total'] = fmt_range(vt)
    tab.at[row, 'Monotherapy'] = fmt_range(vm)
    tab.at[row, 'Combination'] = fmt_range(vc)
    tab.at[row, 'p-value'] = fmt_p(p)
    tab.at[row, 'Test'] = test
    return vt, vm, vc, p, test


def add_flags_extended(df: pd.DataFrame) -> pd.DataFrame:
    df['age_vec'] = pd.to_numeric(df[COL_AGE], errors='coerce')
    df['flag_female'] = df[COL_SEX].astype(str).str.lower().str.startswith('f')
    dis = df['baseline disease']
    df['heme'] = dis.map(heme_subtype)
    df['auto'] = dis.map(auto_subtype)
    df['trans'] = dis.map(transp_subtype)
    df['group'] = df[COL_DIS].map(disease_group)
    df['immu'] = df[COL_BASE].map(immuno_cat)
    s = df[COL_DIS].astype(str).str.lower()
    df['flag_malign'] = s.str.contains('m')
    df['flag_autoimm'] = s.str.contains('a')
    df['flag_transpl'] = s.str.contains('t')
    base = df[COL_BASE].map(group_immuno)
    df['flag_cd20'] = base == 'CD20'
    df['flag_cart'] = base == 'CAR-T'
    df['flag_hsct'] = base == 'HSCT'
    df['flag_immuno_none'] = ~(
        df[['flag_cd20', 'flag_cart', 'flag_hsct']].any(axis=1)
    ) | (base == 'none')
    df['flag_gc'] = df[COL_GC].astype(str).str.lower().str.startswith('y')
    vacc = df[COL_VACC].map(parse_vacc)
    df['vacc_yes'] = vacc.map(lambda x: x[0] == 'Yes')
    df['dose_vec'] = vacc.map(lambda x: x[1])
    df['flag_ct'] = df[COL_CT].astype(str).str.lower().str.startswith('y')
    df['flag_hosp'] = df[COL_HOSP].astype(str).str.lower().str.startswith('y')
    df['rep_vec'] = pd.to_numeric(df[COL_REP], errors='coerce')
    df['geno'] = df[COL_GENO].map(geno_cat)
    df['flag_long'] = df['rep_vec'] >= 14
    df['flag_surv'] = df[COL_SURV].astype(str).str.lower().str.startswith('y')
    df['adv'] = df[COL_AE_TYPE].map(ae_cat)
    return df


add_flags_extended(TOTAL)
add_flags_extended(MONO)
add_flags_extended(COMBO)


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
