# data_preprocessing.py
import pandas as pd
import numpy as np
import re
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu, shapiro, ttest_ind


def normalize_text(x):
    return str(x).lower().strip()


NONE_SET = {"none", "nan", "n/a", "na", ""}
OTHER_AV_NAMES = [
    "azd7442",
    "tix",
    "cil",
    "sot",
    "cas",
    "imd",
    "beb",
    "ens",
    "favipiravir",
    "entecavir",
]
HEME_SYNONYMES = {
    "non-hodgkin lymphoma": "NHL",
    "non hodgkin lymphoma": "NHL",
    "follicular": "FL",
    "fcl": "FL",
}
AUTO_SYNONYMES = {
    "rheum. arthritis": "RA",
    "rheumatoid arthritis": "RA",
    "ra": "RA",
}
FILE_PATH = 'data_characteristics_v10.xlsx'
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
try:
    ABBREV_DF = pd.read_excel(
        FILE_PATH,
        sheet_name='primary cohort, n=104',
        usecols='H:I',
        header=106,
    ).dropna(how='all')
    ABBREV_DF.columns = ['Abbreviation', 'Full Form']
except Exception:
    ABBREV_DF = pd.DataFrame(columns=['Abbreviation', 'Full Form'])
for _df in (TOTAL, MONO, COMBO):
    if 'baseline therapy cohort' in _df.columns and COL_BASE not in _df.columns:
        _df.rename(columns={'baseline therapy cohort': COL_BASE}, inplace=True)
    for c in list(_df.columns):
        if c.startswith('2nd line extended Paxlovid treatment'):
            _df.rename(columns={c: COL_EXT}, inplace=True)
    s = _df[COL_OTHER].map(normalize_text)
    s_clean = s.str.replace(r'\s+', '', regex=True)
    _df['flag_pax5d'] = pd.to_numeric(_df[COL_NMV_STD], errors='coerce').fillna(0) > 0
    _df['flag_rdv'] = s.str.contains('rdv') | s.str.contains('remdesivir')
    _df['flag_mpv'] = s.str.contains('mpv') | s.str.contains('molnupiravir')
    mask = pd.Series(False, index=_df.index)
    for name in OTHER_AV_NAMES:
        mask |= s_clean.str.contains(name.replace(' ', ''), na=False)
    det = mask
    _df['flag_other'] = (
        (~_df['flag_rdv'] & ~_df['flag_mpv'] & det & ~_df['flag_pax5d'])
        | (~_df['flag_rdv'] & ~_df['flag_mpv'] & _df['flag_pax5d'] & det)
        | (_df['flag_rdv'] & _df['flag_mpv'] & _df['flag_pax5d'] & det)
    )
    _df['flag_none'] = ~(
        _df['flag_pax5d'] | _df['flag_rdv'] | _df['flag_mpv'] | _df['flag_other']
    )
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
    if (exp < 5).any() or min(a11 + a12, a21 + a22) < 25:
        return fisher_exact([[a11, a12], [a21, a22]])[1]
    return chi2_contingency([[a11, a12], [a21, a22]])[1]


def cont_test(v1, v2):
    if shapiro(v1).pvalue >= 0.05 and shapiro(v2).pvalue >= 0.05:
        return ttest_ind(v1, v2, equal_var=False).pvalue
    return mannwhitneyu(v1, v2).pvalue


def parse_yn(x):
    s = normalize_text(x)
    if s in NONE_SET:
        return np.nan
    if s.startswith("y"):
        return True
    if s.startswith("n"):
        return False
    return np.nan


def parse_has(x, ch):
    s = normalize_text(x)
    if s in NONE_SET:
        return np.nan
    return ch in s


def parse_female(x):
    s = normalize_text(x)
    if s in NONE_SET:
        return np.nan
    if s.startswith("f"):
        return True
    if s.startswith("m"):
        return False
    return np.nan


def parse_vacc(x: str):
    s = normalize_text(x)
    m = pd.Series(s).str.extract(r'(\d+)')[0]
    dose = float(m.iloc[0]) if m.notna().any() else np.nan
    if s in NONE_SET:
        return 'Unknown', dose
    if s.startswith('y'):
        return 'Yes', dose
    if s.startswith('n'):
        return 'No', dose
    return 'Unknown', dose


def heme_subtype(x):
    s = normalize_text(x).replace('-', ' ')
    if ',' in s or '+' in s:
        return 'Mixed'
    for k, v in HEME_SYNONYMES.items():
        if k in s:
            return v
    if 'dlbcl' in s:
        return 'DLBCL'
    if 'all' in s:
        return 'ALL'
    if 'cll' in s and ',' not in s and '+' not in s:
        return 'CLL'
    if 'aml' in s:
        return 'AML'
    if 'follicular' in s or s.strip() == 'fl' or ' fl' in s:
        return 'FL'
    if 'nhl' in s or 'lymphoma' in s:
        return 'NHL'
    if 'mcl' in s or 'lpl' in s or 'malt' in s:
        return 'Other'
    if 'mm' in s or 'pcl' in s or 'myeloma' in s:
        return 'MM'
    if s.strip() == 'nos':
        return 'NOS'
    if s.strip():
        return 'Other'
    return None


def auto_subtype(x):
    s = normalize_text(x)
    if (
        'anca' in s
        or 'mcd' in s
        or 'mctd' in s
        or 'nmda' in s
        or 'crest' in s
        or s.strip() in {'ssc, lt', 'kt, cu'}
    ):
        return 'Other'
    for k, v in AUTO_SYNONYMES.items():
        if k in s:
            return v
    if 'ms' in s and 'mcl' not in s:
        return 'MS'
    if 'systemic sclerosis' in s or re.search(r'\bssc\b', s):
        return 'SSc'
    if 'ulcerosa' in s:
        return 'Colitis ulcerosa'
    if 'glomerulonephritis' in s:
        return 'Glomerulonephritis'
    return None


def transp_subtype(x):
    s = str(x).lower()
    if re.search(r'\blt\b', s) or ('lung' in s and 'tx' in s):
        return 'LT'
    if re.search(r'\bkt\b', s) or ('kidney' in s and 'tx' in s):
        return 'KT'
    return None


def disease_group(x):
    s = normalize_text(x)
    if s in NONE_SET:
        return None
    if 'm' in s:
        return 'Haematological malignancy'
    if 't' in s:
        return 'Transplantation'
    if 'a' in s:
        return 'Autoimmune disease'
    return None


def classify_immuno(x):
    s = normalize_text(x)
    if s in NONE_SET:
        return 'None'
    has_cd20 = 'cd20' in s
    has_car = 'car' in s
    has_hsct = 'hsct' in s
    if sum([has_cd20, has_car, has_hsct]) > 1:
        return 'Mixed'
    if has_cd20:
        return 'Anti-CD20'
    if has_car:
        return 'CAR-T'
    if has_hsct:
        return 'HSCT'
    return 'Other'


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
        return 'BA.5'
    if 'ba.2' in s or s.startswith(('ba2', 'xd', 'xay')):
        return 'BA.2'
    if 'ba.1' in s or s.startswith('ba1'):
        return 'BA.1'
    if s:
        return 'Other'
    return None


def ae_cat(x):
    s = normalize_text(x)
    if 'thrombocytopenia' in s:
        return 'Thrombocytopenia'
    if not s or s in NONE_SET or s == 'n':
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
    ft = ft.dropna()
    fm = fm.dropna()
    fc = fc.dropna()
    nt = int(ft.sum())
    nm = int(fm.sum())
    nc = int(fc.sum())
    p = chi_or_fisher(nc, len(fc) - nc, nm, len(fm) - nm)
    return nt, nm, nc, len(ft), len(fm), len(fc), p


def vec_calc(vt, vm, vc):
    vt = pd.to_numeric(vt, errors='coerce').dropna()
    vm = pd.to_numeric(vm, errors='coerce').dropna()
    vc = pd.to_numeric(vc, errors='coerce').dropna()
    return vt, vm, vc, cont_test(vm, vc)


def fill_rate(tab, row, ft, fm, fc, blank=False):
    nt, nm, nc, dt, dm, dc, p = rate_calc(ft, fm, fc)
    tab.at[row, 'Total'] = fmt_pct(nt, dt)
    tab.at[row, 'Monotherapy'] = fmt_pct(nm, dm)
    tab.at[row, 'Combination'] = fmt_pct(nc, dc)
    tab.at[row, 'p-value'] = '' if blank and nt == 0 else fmt_p(p)
    return nt, nm, nc, p


def fill_median_iqr(tab, row, vt, vm, vc):
    vt, vm, vc, p = vec_calc(vt, vm, vc)
    tab.at[row, 'Total'] = fmt_iqr(vt)
    tab.at[row, 'Monotherapy'] = fmt_iqr(vm)
    tab.at[row, 'Combination'] = fmt_iqr(vc)
    tab.at[row, 'p-value'] = fmt_p(p)
    return vt, vm, vc, p


def fill_mean_range(tab, row, vt, vm, vc):
    vt, vm, vc, p = vec_calc(vt, vm, vc)
    tab.at[row, 'Total'] = f'{vt.mean():.1f} ({fmt_range(vt)})'
    tab.at[row, 'Monotherapy'] = f'{vm.mean():.1f} ({fmt_range(vm)})'
    tab.at[row, 'Combination'] = f'{vc.mean():.1f} ({fmt_range(vc)})'
    tab.at[row, 'p-value'] = fmt_p(p)
    return vt, vm, vc, p


def fill_range(tab, row, vt, vm, vc):
    vt, vm, vc, p = vec_calc(vt, vm, vc)
    tab.at[row, 'Total'] = fmt_range(vt)
    tab.at[row, 'Monotherapy'] = fmt_range(vm)
    tab.at[row, 'Combination'] = fmt_range(vc)
    tab.at[row, 'p-value'] = fmt_p(p)
    return vt, vm, vc, p


def add_flags_extended(df: pd.DataFrame) -> pd.DataFrame:
    df['age_vec'] = pd.to_numeric(df[COL_AGE], errors='coerce')
    df['flag_female'] = df[COL_SEX].map(parse_female)
    dis = df['baseline disease']
    df['heme'] = dis.map(heme_subtype)
    df['auto'] = dis.map(auto_subtype)
    df['trans'] = dis.map(transp_subtype)
    df['group'] = df[COL_DIS].map(disease_group)
    df['immu'] = df[COL_BASE].map(classify_immuno)
    s = df[COL_DIS]
    df['flag_malign'] = s.map(lambda x: parse_has(x, 'm'))
    df['flag_autoimm'] = s.map(lambda x: parse_has(x, 'a'))
    df['flag_transpl'] = s.map(lambda x: parse_has(x, 't'))
    df['flag_cd20'] = df['immu'] == 'Anti-CD20'
    df['flag_cart'] = df['immu'] == 'CAR-T'
    df['flag_hsct'] = df['immu'] == 'HSCT'
    df['flag_immuno_none'] = df['immu'] == 'None'
    df['flag_immuno_mixed'] = df['immu'] == 'Mixed'
    df['flag_immuno_other'] = df['immu'] == 'Other'
    df['flag_gc'] = df[COL_GC].map(parse_yn)
    vacc = df[COL_VACC].map(parse_vacc)
    df['vacc_yes'] = vacc.map(lambda x: x[0] == 'Yes')
    df['dose_vec'] = vacc.map(lambda x: x[1])
    df['flag_ct'] = df[COL_CT].map(parse_yn)
    df['flag_hosp'] = df[COL_HOSP].map(parse_yn)
    df['rep_vec'] = pd.to_numeric(df[COL_REP], errors='coerce')
    df['geno'] = df[COL_GENO].map(geno_cat)
    df['flag_long'] = df['rep_vec'] >= 14
    df['flag_surv'] = df[COL_SURV].map(parse_yn)
    df['adv'] = df[COL_AE_TYPE].map(ae_cat)
    return df


add_flags_extended(TOTAL)
add_flags_extended(MONO)
add_flags_extended(COMBO)


def baseline_stats() -> pd.DataFrame:
    labels = ['Anti-CD20', 'CAR-T', 'HSCT', 'Mixed', 'Other', 'None']
    t = TOTAL[COL_BASE].map(classify_immuno)
    m = MONO[COL_BASE].map(classify_immuno)
    c = COMBO[COL_BASE].map(classify_immuno)
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


def export_abbreviations_md(path: str) -> None:
    ABBREV_DF.to_markdown(path, index=False)


if __name__ == '__main__':
    print(TOTAL.shape)
    print(MONO.shape)
    print(COMBO.shape)
    print(baseline_stats())

# table_a.py
def build_table_a():
    days_t, courses_t = parse_ext(TOTAL[COL_EXT])
    days_m, courses_m = parse_ext(MONO[COL_EXT])
    days_c, courses_c = parse_ext(COMBO[COL_EXT])
    index = pd.MultiIndex.from_tuples(
        [
            ('N =', ''),
            ('First-line therapy\u00b9, n (%)', ''),
            ('First-line therapy\u00b9, n (%)', 'Remdesivir'),
            ('First-line therapy\u00b9, n (%)', 'Molnupiravir'),
            ('First-line therapy\u00b9, n (%)', 'Standard 5-day Paxlovid'),
            ('First-line therapy\u00b9, n (%)', 'Other antivirals'),
            ('First-line therapy\u00b9, n (%)', 'None'),
            ('Last line therapy\u00b2, n (%)', ''),
            ('Last line therapy\u00b2, n (%)', 'Combination therapy'),
            ('Last line therapy\u00b2, n (%)', 'Monotherapy'),
            ('Treatment courses, n (%)', ''),
            ('Treatment courses, n (%)', 'Single prolonged course'),
            ('Treatment courses, n (%)', 'Multiple courses'),
            ('Duration', ''),
            ('Duration', 'Median duration, days (IQR)'),
            ('Duration', 'Duration range, days'),
        ],
        names=['Category', 'Subcategory'],
    )
    t_x = pd.DataFrame(index=index, columns=[
        'Total',
        'Monotherapy',
        'Combination',
        'p-value',
    ])
    t_x.loc[('N =', '')] = [len(TOTAL), len(MONO), len(COMBO), '']

    def add_rate(row, st, sm, sc):
        fill_rate(t_x, row, st, sm, sc, blank=False)

    labels = [
        'Standard 5-day Paxlovid',
        'Remdesivir',
        'Molnupiravir',
        'Other antivirals',
    ]
    cols = ['flag_pax5d', 'flag_rdv', 'flag_mpv', 'flag_other']
    for lbl, col in zip(labels, cols):
        add_rate(
            ('First-line therapy\u00b9, n (%)', lbl),
            TOTAL[col],
            MONO[col],
            COMBO[col],
        )
    add_rate(
        ('First-line therapy\u00b9, n (%)', 'None'),
        TOTAL['flag_none'],
        MONO['flag_none'],
        COMBO['flag_none'],
    )
    t_x.loc[('First-line therapy\u00b9, n (%)', '')] = ''
    com_flag_t = TOTAL[COL_THERAPY].str.startswith('c', na=False)
    mono_flag_t = TOTAL[COL_THERAPY].str.startswith('m', na=False)
    idx = ('Last line therapy\u00b2, n (%)', 'Combination therapy')
    t_x.at[idx, 'Total'] = fmt_pct(int(com_flag_t.sum()), len(TOTAL))
    t_x.at[idx, 'Monotherapy'] = fmt_pct(0, len(MONO))
    t_x.at[idx, 'Combination'] = fmt_pct(len(COMBO), len(COMBO))
    p_last = chi_or_fisher(len(COMBO), 0, 0, len(MONO))
    t_x.at[idx, 'p-value'] = ''
    idx = ('Last line therapy\u00b2, n (%)', 'Monotherapy')
    t_x.at[idx, 'Total'] = fmt_pct(int(mono_flag_t.sum()), len(TOTAL))
    t_x.at[idx, 'Monotherapy'] = fmt_pct(len(MONO), len(MONO))
    t_x.at[idx, 'Combination'] = fmt_pct(0, len(COMBO))
    t_x.at[idx, 'p-value'] = ''
    t_x.loc[('Last line therapy\u00b2, n (%)', '')] = ''
    t_x.at[('Last line therapy\u00b2, n (%)', ''), 'p-value'] = fmt_p(p_last)
    single_t = courses_t == 1
    multi_t = courses_t > 1
    single_m = courses_m == 1
    multi_m = courses_m > 1
    single_c = courses_c == 1
    multi_c = courses_c > 1
    row = ('Treatment courses, n (%)', 'Single prolonged course')
    t_x.at[row, 'Total'] = fmt_pct(int(single_t.sum()), len(TOTAL))
    t_x.at[row, 'Monotherapy'] = fmt_pct(int(single_m.sum()), len(MONO))
    t_x.at[row, 'Combination'] = fmt_pct(int(single_c.sum()), len(COMBO))
    row = ('Treatment courses, n (%)', 'Multiple courses')
    t_x.at[row, 'Total'] = fmt_pct(int(multi_t.sum()), len(TOTAL))
    t_x.at[row, 'Monotherapy'] = fmt_pct(int(multi_m.sum()), len(MONO))
    t_x.at[row, 'Combination'] = fmt_pct(int(multi_c.sum()), len(COMBO))
    p_course = chi_or_fisher(int(single_c.sum()), int(multi_c.sum()), int(single_m.sum()), int(multi_m.sum()))
    t_x.at[('Treatment courses, n (%)', 'Single prolonged course'), 'p-value'] = ''
    t_x.at[('Treatment courses, n (%)', 'Multiple courses'), 'p-value'] = ''
    t_x.loc[('Treatment courses, n (%)', '')] = ''
    t_x.at[('Treatment courses, n (%)', ''), 'p-value'] = fmt_p(p_course)
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'Total'] = fmt_iqr(days_t)
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'Monotherapy'] = fmt_iqr(days_m)
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'Combination'] = fmt_iqr(days_c)
    t_x.at[('Duration', 'Duration range, days'), 'Total'] = fmt_range(days_t)
    t_x.at[('Duration', 'Duration range, days'), 'Monotherapy'] = fmt_range(days_m)
    t_x.at[('Duration', 'Duration range, days'), 'Combination'] = fmt_range(days_c)
    t_x.loc[('Duration', '')] = ''
    p_dur = cont_test(days_m.dropna(), days_c.dropna())
    t_x.at[('Duration', ''), 'p-value'] = fmt_p(p_dur)
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'p-value'] = ''
    t_x.at[('Duration', 'Duration range, days'), 'p-value'] = ''
    foot = (
        '- NMV-r, nirmatrelvir-ritonavir.\n'
        '1: Any treatment administered prior to extended nirmatrelvir-ritonavir, '
        'including standard 5-day Paxlovid courses with or without other antivirals.\n'
        '2: Extended nirmatrelvir-ritonavir regimens (with or without concurrent antivirals) '
        'when no subsequent antiviral therapy was administered.'
    )
    t_x.attrs['footnote'] = foot
    return t_x


def build_table_a_raw():
    days_t, courses_t = parse_ext(TOTAL[COL_EXT])
    days_m, courses_m = parse_ext(MONO[COL_EXT])
    days_c, courses_c = parse_ext(COMBO[COL_EXT])
    index = pd.MultiIndex.from_tuples(
        [
            ('First-line therapy\u00b9, n', 'Remdesivir'),
            ('First-line therapy\u00b9, n', 'Molnupiravir'),
            ('First-line therapy\u00b9, n', 'Standard 5-day Paxlovid'),
            ('First-line therapy\u00b9, n', 'Other antivirals'),
            ('First-line therapy\u00b9, n', 'None'),
            ('Last line therapy\u00b2, n', 'Combination therapy'),
            ('Last line therapy\u00b2, n', 'Monotherapy'),
            ('Treatment courses, n', 'Single prolonged course'),
            ('Treatment courses, n', 'Multiple courses'),
            ('Duration, days', 'Median'),
            ('Duration, days', 'Min'),
            ('Duration, days', 'Max'),
        ],
        names=['Category', 'Subcategory'],
    )
    raw = pd.DataFrame(index=index, columns=[
        'Total',
        'Monotherapy',
        'Combination',
        'p-value',
    ])

    def add(row, st, sm, sc):
        nt, nm, nc, p = rate_calc(st, sm, sc)
        raw.at[row, 'Total'] = nt
        raw.at[row, 'Monotherapy'] = nm
        raw.at[row, 'Combination'] = nc
        if nt:
            raw.at[row, 'p-value'] = p

    labels = [
        'Standard 5-day Paxlovid',
        'Remdesivir',
        'Molnupiravir',
        'Other antivirals',
    ]
    cols = ['flag_pax5d', 'flag_rdv', 'flag_mpv', 'flag_other']
    for lbl, col in zip(labels, cols):
        add(('First-line therapy\u00b9, n', lbl), TOTAL[col], MONO[col], COMBO[col])
    add(
        ('First-line therapy\u00b9, n', 'None'),
        TOTAL['flag_none'],
        MONO['flag_none'],
        COMBO['flag_none'],
    )
    com_flag_t = TOTAL[COL_THERAPY].str.startswith('c', na=False)
    mono_flag_t = TOTAL[COL_THERAPY].str.startswith('m', na=False)
    add(
        ('Last line therapy\u00b2, n', 'Combination therapy'),
        com_flag_t,
        MONO[COL_THERAPY].str.startswith('c', na=False),
        COMBO[COL_THERAPY].str.startswith('c', na=False),
    )
    raw.at[('Last line therapy\u00b2, n', 'Combination therapy'), 'p-value'] = chi_or_fisher(
        len(COMBO),
        0,
        0,
        len(MONO),
    )
    raw.at[('Last line therapy\u00b2, n', 'Monotherapy'), 'Total'] = int(mono_flag_t.sum())
    raw.at[('Last line therapy\u00b2, n', 'Monotherapy'), 'Monotherapy'] = len(MONO)
    raw.at[('Last line therapy\u00b2, n', 'Monotherapy'), 'Combination'] = 0
    raw.at[('Last line therapy\u00b2, n', 'Monotherapy'), 'p-value'] = None
    single_t = courses_t == 1
    multi_t = courses_t > 1
    single_m = courses_m == 1
    multi_m = courses_m > 1
    single_c = courses_c == 1
    multi_c = courses_c > 1
    add(('Treatment courses, n', 'Single prolonged course'), single_t, single_m, single_c)
    raw.at[('Treatment courses, n', 'Multiple courses'), 'Total'] = int(multi_t.sum())
    raw.at[('Treatment courses, n', 'Multiple courses'), 'Monotherapy'] = int(multi_m.sum())
    raw.at[('Treatment courses, n', 'Multiple courses'), 'Combination'] = int(multi_c.sum())
    p_course = chi_or_fisher(int(single_c.sum()), int(multi_c.sum()), int(single_m.sum()), int(multi_m.sum()))
    raw.at[('Treatment courses, n', 'Single prolonged course'), 'p-value'] = p_course
    raw.at[('Treatment courses, n', 'Multiple courses'), 'p-value'] = None
    raw.at[('Duration, days', 'Median'), 'Total'] = days_t.median()
    raw.at[('Duration, days', 'Median'), 'Monotherapy'] = days_m.median()
    raw.at[('Duration, days', 'Median'), 'Combination'] = days_c.median()
    raw.at[('Duration, days', 'Min'), 'Total'] = days_t.min()
    raw.at[('Duration, days', 'Min'), 'Monotherapy'] = days_m.min()
    raw.at[('Duration, days', 'Min'), 'Combination'] = days_c.min()
    raw.at[('Duration, days', 'Max'), 'Total'] = days_t.max()
    raw.at[('Duration, days', 'Max'), 'Monotherapy'] = days_m.max()
    raw.at[('Duration, days', 'Max'), 'Combination'] = days_c.max()
    raw.at[('Duration, days', 'Median'), 'p-value'] = cont_test(days_m.dropna(), days_c.dropna())
    raw.at[('Duration, days', 'Min'), 'p-value'] = raw.at[('Duration, days', 'Median'), 'p-value']
    raw.at[('Duration, days', 'Max'), 'p-value'] = raw.at[('Duration, days', 'Median'), 'p-value']
    foot = (
        '- NMV-r, nirmatrelvir-ritonavir.\n'
        '1: Any treatment administered prior to extended nirmatrelvir-ritonavir, '
        'including standard 5-day Paxlovid courses with or without other antivirals.\n'
        '2: Extended nirmatrelvir-ritonavir regimens (with or without concurrent antivirals) '
        'when no subsequent antiviral therapy was administered.'
    )
    raw.attrs['footnote'] = foot
    return raw


if __name__ == '__main__':
    print('Table A. Treatment Approach.')
    print(build_table_a().to_string())
    print('- NMV-r, nirmatrelvir-ritonavir.')
    print(
        '1: Any treatment administered prior to extended nirmatrelvir-ritonavir, '
        'including standard 5-day Paxlovid courses with or without other antivirals.'
    )
    print(
        '2: Extended nirmatrelvir-ritonavir regimens (with or without concurrent antivirals) '
        'when no subsequent antiviral therapy was administered.'
    )

# table_b.py
index = pd.MultiIndex.from_tuples(
    [
        ('N =', ''),
        ('Age, median (IQR)', ''),
        ('Female sex, n (%)', ''),
        ('Underlying conditions, n (%)', ''),
        ('Underlying conditions, n (%)', 'Hematological malignancy'),
        ('Underlying conditions, n (%)', 'Autoimmune'),
        ('Underlying conditions, n (%)', 'Transplantation'),
        ('Immunosuppressive treatment, n (%)', ''),
        ('Immunosuppressive treatment, n (%)', 'Anti-CD20'),
        ('Immunosuppressive treatment, n (%)', 'CAR-T'),
        ('Immunosuppressive treatment, n (%)', 'HSCT'),
        ('Immunosuppressive treatment, n (%)', 'Mixed'),
        ('Immunosuppressive treatment, n (%)', 'Other\u00b2'),
        ('Immunosuppressive treatment, n (%)', 'None'),
        ('Glucocorticoid use, n (%)', ''),
        ('SARS-CoV-2 vaccination, n (%)', ''),
        ('Mean Vaccination doses, n (range)', ''),
        ('Thoracic CT changes, n (%)', ''),
        ('Treatment setting\u00b9, n (%)', ''),
        ('Treatment setting\u00b9, n (%)', 'Hospital'),
        ('Treatment setting\u00b9, n (%)', 'Outpatient'),
    ],
    names=['Category', 'Subcategory'],
)

columns = [
    'Total',
    'Monotherapy',
    'Combination',
    'p-value',
]

table_b = pd.DataFrame(index=index, columns=columns)
table_b_raw = pd.DataFrame(index=index, columns=columns)
table_b.loc[('N =', '')] = [len(TOTAL), len(MONO), len(COMBO), '']
table_b_raw.loc[('N =', '')] = [len(TOTAL), len(MONO), len(COMBO), None]


def add_rate(row, ft, fm, fc):
    nt, nm, nc, p = fill_rate(table_b, row, ft, fm, fc)
    table_b_raw.at[row, 'Total'] = nt
    table_b_raw.at[row, 'Monotherapy'] = nm
    table_b_raw.at[row, 'Combination'] = nc
    table_b_raw.at[row, 'p-value'] = p


def add_median_iqr(row, vt, vm, vc):
    vt, vm, vc, p = fill_median_iqr(table_b, row, vt, vm, vc)
    table_b_raw.at[row, 'Total'] = vt.median()
    table_b_raw.at[row, 'Monotherapy'] = vm.median()
    table_b_raw.at[row, 'Combination'] = vc.median()
    table_b_raw.at[row, 'p-value'] = p


def add_mean_range(row, vt, vm, vc):
    vt, vm, vc, p = fill_mean_range(table_b, row, vt, vm, vc)
    table_b_raw.at[row, 'Total'] = vt.mean()
    table_b_raw.at[row, 'Monotherapy'] = vm.mean()
    table_b_raw.at[row, 'Combination'] = vc.mean()
    table_b_raw.at[row, 'p-value'] = p


def build_table_b():
    table_b.loc[:] = None
    table_b_raw.loc[:] = None
    table_b.loc[('N =', '')] = [len(TOTAL), len(MONO), len(COMBO), '']
    table_b_raw.loc[('N =', '')] = [len(TOTAL), len(MONO), len(COMBO), None]
    add_median_iqr(('Age, median (IQR)', ''), TOTAL['age_vec'], MONO['age_vec'], COMBO['age_vec'])
    add_rate(('Female sex, n (%)', ''), TOTAL['flag_female'], MONO['flag_female'], COMBO['flag_female'])
    table_b.loc[('Underlying conditions, n (%)', '')] = ''
    table_b_raw.loc[('Underlying conditions, n (%)', '')] = None
    pairs = [
        ('Hematological malignancy', 'flag_malign'),
        ('Autoimmune', 'flag_autoimm'),
        ('Transplantation', 'flag_transpl'),
    ]
    for lbl, col in pairs:
        add_rate(('Underlying conditions, n (%)', lbl), TOTAL[col], MONO[col], COMBO[col])
    table_b.loc[('Immunosuppressive treatment, n (%)', '')] = ''
    table_b_raw.loc[('Immunosuppressive treatment, n (%)', '')] = None
    pairs = [
        ('Anti-CD20', 'flag_cd20'),
        ('CAR-T', 'flag_cart'),
        ('HSCT', 'flag_hsct'),
        ('Mixed', 'flag_immuno_mixed'),
        ('Other\u00b2', 'flag_immuno_other'),
        ('None', 'flag_immuno_none'),
    ]
    for lbl, col in pairs:
        add_rate(('Immunosuppressive treatment, n (%)', lbl), TOTAL[col], MONO[col], COMBO[col])
    add_rate(('Glucocorticoid use, n (%)', ''), TOTAL['flag_gc'], MONO['flag_gc'], COMBO['flag_gc'])
    add_rate(('SARS-CoV-2 vaccination, n (%)', ''), TOTAL['vacc_yes'], MONO['vacc_yes'], COMBO['vacc_yes'])
    add_mean_range(
        ('Mean Vaccination doses, n (range)', ''),
        TOTAL['dose_vec'],
        MONO['dose_vec'],
        COMBO['dose_vec'],
    )
    add_rate(('Thoracic CT changes, n (%)', ''), TOTAL['flag_ct'], MONO['flag_ct'], COMBO['flag_ct'])

    table_b.loc[('Treatment setting\u00b9, n (%)', '')] = ''
    table_b_raw.loc[('Treatment setting\u00b9, n (%)', '')] = None
    nt, nm, nc, p_set = fill_rate(
        table_b,
        ('Treatment setting\u00b9, n (%)', 'Hospital'),
        TOTAL['flag_hosp'],
        MONO['flag_hosp'],
        COMBO['flag_hosp'],
    )
    table_b_raw.at[('Treatment setting\u00b9, n (%)', 'Hospital'), 'Total'] = nt
    table_b_raw.at[('Treatment setting\u00b9, n (%)', 'Hospital'), 'Monotherapy'] = nm
    table_b_raw.at[('Treatment setting\u00b9, n (%)', 'Hospital'), 'Combination'] = nc
    table_b_raw.at[('Treatment setting\u00b9, n (%)', 'Hospital'), 'p-value'] = p_set
    nt2, nm2, nc2, _ = fill_rate(
        table_b,
        ('Treatment setting\u00b9, n (%)', 'Outpatient'),
        ~TOTAL['flag_hosp'],
        ~MONO['flag_hosp'],
        ~COMBO['flag_hosp'],
    )
    table_b_raw.at[('Treatment setting\u00b9, n (%)', 'Outpatient'), 'Total'] = nt2
    table_b_raw.at[('Treatment setting\u00b9, n (%)', 'Outpatient'), 'Monotherapy'] = nm2
    table_b_raw.at[('Treatment setting\u00b9, n (%)', 'Outpatient'), 'Combination'] = nc2
    table_b_raw.at[('Treatment setting\u00b9, n (%)', 'Outpatient'), 'p-value'] = None
    table_b.at[('Treatment setting\u00b9, n (%)', 'Hospital'), 'p-value'] = ''
    table_b.at[('Treatment setting\u00b9, n (%)', 'Outpatient'), 'p-value'] = ''
    table_b.at[('Treatment setting\u00b9, n (%)', ''), 'p-value'] = fmt_p(p_set)
    vals = (
        TOTAL.loc[TOTAL['flag_immuno_other'], COL_BASE]
        .dropna()
        .unique()
    )
    extra = '; '.join(str(v) for v in vals)
    foot = (
        '- NMV-r, nirmatrelvir-ritonavir.\n'
        '1: Treatment setting where prolonged NMV-r was administered.\n'
        f'2: Other immunosuppressive treatment includes: {extra}.'
    )
    table_b.attrs['footnote'] = foot
    table_b_raw.attrs['footnote'] = foot
    return table_b


def build_table_b_raw():
    if table_b_raw.isnull().all().all():
        build_table_b()
    return table_b_raw


if __name__ == '__main__':
    tab = build_table_b()
    tab.to_excel('table_b_v7.xlsx')
    build_table_b_raw().to_csv('table_b_v7.csv')
    print(tab.shape)
    print('Table B. Demographics and Clinical Characteristics.')
    print(build_table_b().to_string())
    print('- NMV-r, nirmatrelvir-ritonavir.')
    print('1: Treatment setting where prolonged NMV-r was administered.')

__all__ = [
    'table_b',
    'table_b_raw',
    'TOTAL',
    'MONO',
    'COMBO',
    'build_table_b',
    'build_table_b_raw',
    'add_rate',
    'add_median_iqr',
    'add_mean_range',
]

# table_c.py
index = pd.MultiIndex.from_tuples(
    [
        ('Haematological malignancy, n (%)', ''),
        ('Haematological malignancy, n (%)', 'FL'),
        ('Haematological malignancy, n (%)', 'NHL'),
        ('Haematological malignancy, n (%)', 'Other\u00b9'),
        ('Autoimmune disease, n (%)', ''),
        ('Autoimmune disease, n (%)', 'RA'),
        ('Autoimmune disease, n (%)', 'Other\u00b2'),
        ('Transplantation, n (%)', ''),
        ('Transplantation, n (%)', 'LT'),
        ('Transplantation, n (%)', 'KT'),
        ('Duration of SARS-CoV-2 replication (days), median (IQR)', ''),
        ('SARS-CoV-2 genotype, n (%)', ''),
        ('SARS-CoV-2 genotype, n (%)', 'BA.5'),
        ('SARS-CoV-2 genotype, n (%)', 'BA.2'),
        ('SARS-CoV-2 genotype, n (%)', 'BA.1'),
        ('SARS-CoV-2 genotype, n (%)', 'Other'),
        ('Prolonged viral shedding (\u2265\u202f14\u202fdays), n (%)', ''),
        ('Survival, n (%)', ''),
        ('Adverse events, n (%)', ''),
        ('Adverse events, n (%)', 'None'),
        ('Adverse events, n (%)', 'Thrombocytopenia'),
        ('Adverse events, n (%)', 'Other'),
    ],
    names=['Category', 'Subcategory'],
)

columns = [
    'Total',
    'Monotherapy',
    'Combination',
    'p-value',
]

table_c = pd.DataFrame(index=index, columns=columns)


def add_rate(row, ft, fm, fc):
    fill_rate(table_c, row, ft, fm, fc)


def add_median_iqr(row, vt, vm, vc):
    fill_median_iqr(table_c, row, vt, vm, vc)


def add_range(row, vt, vm, vc):
    fill_range(table_c, row, vt, vm, vc)


def build_table_c():
    table_c.loc[:] = None
    table_c.loc[('Haematological malignancy, n (%)', '')] = ''
    table_c.loc[('Autoimmune disease, n (%)', '')] = ''
    table_c.loc[('Transplantation, n (%)', '')] = ''
    table_c.loc[('SARS-CoV-2 genotype, n (%)', '')] = ''
    table_c.loc[('Adverse events, n (%)', '')] = ''
    labs = ['FL', 'NHL', 'Other\u00b9']
    for lab in labs:
        db_lab = 'Other' if lab == 'Other\u00b9' else lab
        add_rate(
            ('Haematological malignancy, n (%)', lab),
            TOTAL['heme'] == db_lab,
            MONO['heme'] == db_lab,
            COMBO['heme'] == db_lab,
        )
    labs = ['RA', 'Other\u00b2']
    for lab in labs:
        db_lab = 'Other' if lab == 'Other\u00b2' else lab
        add_rate(
            ('Autoimmune disease, n (%)', lab),
            TOTAL['auto'] == db_lab,
            MONO['auto'] == db_lab,
            COMBO['auto'] == db_lab,
        )
    for lab in ['LT', 'KT']:
        add_rate(
            ('Transplantation, n (%)', lab),
            TOTAL['trans'] == lab,
            MONO['trans'] == lab,
            COMBO['trans'] == lab,
        )
    add_median_iqr(
        ('Duration of SARS-CoV-2 replication (days), median (IQR)', ''),
        TOTAL['rep_vec'],
        MONO['rep_vec'],
        COMBO['rep_vec'],
    )
    labs = [
        'BA.5',
        'BA.2',
        'BA.1',
        'Other',
    ]
    for lab in labs:
        add_rate(
            ('SARS-CoV-2 genotype, n (%)', lab),
            TOTAL['geno'] == lab,
            MONO['geno'] == lab,
            COMBO['geno'] == lab,
        )
    add_rate(
        ('Prolonged viral shedding (\u2265\u202f14\u202fdays), n (%)', ''),
        TOTAL['flag_long'],
        MONO['flag_long'],
        COMBO['flag_long'],
    )
    add_rate(
        ('Survival, n (%)', ''),
        TOTAL['flag_surv'],
        MONO['flag_surv'],
        COMBO['flag_surv'],
    )
    for lab in ['None', 'Thrombocytopenia', 'Other']:
        add_rate(('Adverse events, n (%)', lab), TOTAL['adv'] == lab, MONO['adv'] == lab, COMBO['adv'] == lab)
    table_c.attrs['footnote'] = (
        '1: Other includes MCL, LPL, MALT lymphoma and similar entities.'
        '\n2: Other includes ANCA-Vasculitis, CREST, MCD, MCTD, '
        'NMDA-encephalitis, SSc, LT, KT, CU.'
    )
    return table_c


if __name__ == '__main__':
    print('Table C. Detailed Patient Characteristics.')
    print(build_table_c().to_string())

# table_d.py
COL_ERAD = 'eradication outcome successful\n[yes / no]'
COL_SURV = 'survival outcome\n[yes / no]'
COL_AE_YN = 'any adverse events\n[yes / no]'


def flag(series, val):
    s = series.map(parse_yn)
    return s == (val == 'y')


index = [
    'SARS-CoV-2 Persistence\u00b9, n (%)',
    'All-cause mortality\u00b2, n (%)',
    'SARS-CoV-2-related mortality\u00b3, n (%)',
    'AE\u2074, n (%)',
]


def build_table_d():
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
    tab = build_table_d()
    print('Table D. Outcomes in all cohorts.')
    print(tab.to_string())
    foot = tab.attrs['footnote']
    for line in foot.split('\n'):
        if line:
            print(line)

