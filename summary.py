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


def load(name):
    df = pd.read_excel(f"{name}.xlsx")
    return df


def group_disease(x: str) -> str:
    s = str(x).lower()
    a = 'a' in s
    m = 'm' in s
    t = 't' in s
    if sum([a, m, t]) > 1:
        return 'Mixed'
    if m:
        return 'Hematological malignancy'
    if a:
        return 'Autoimmune'
    if t:
        return 'Transplantation'
    return 'Unknown'


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


def flag_gc(x: str) -> str:
    s = str(x).lower()
    if s.startswith('y'):
        return 'Yes'
    if s.startswith('n'):
        return 'No'
    return 'Unknown'


def parse_vacc(x: str):
    s = str(x).lower()
    m = pd.Series(s).str.extract(r'(\d+)')[0]
    dose = float(m) if m.notna().any() else np.nan
    if s.startswith('y'):
        return 'Yes', dose
    if s.startswith('n'):
        return 'No', dose
    return 'Unknown', dose


def group_ct(x: str) -> str:
    s = str(x).lower()
    if s.startswith('y'):
        return 'Yes'
    if s.startswith('n'):
        return 'No'
    return 'Unknown'


def parse_ext(series: pd.Series):
    pattern = r'(\d+(?:\.\d+)?)\s*(?:\(|\[)?(\d+)(?:\)|\])?'
    tmp = series.astype(str).str.extract(pattern)
    days = tmp[0].astype(float)
    courses = tmp[1].astype(float)
    return days, courses


def p_cat(series: pd.Series, labels: pd.Series) -> float:
    table = pd.crosstab(series, labels)
    exp = np.outer(table.sum(axis=1), table.sum(axis=0)) / table.values.sum()
    if series.nunique() == 2:
        if (exp < 5).any():
            return fisher_exact(table)[1]
        return chi2_contingency(table, correction=False)[1]
    if (exp < 5).any():
        cats = pd.Categorical(series)
        obs = chi2_contingency(pd.crosstab(cats, labels), correction=False)[0]
        codes = cats.codes
        labs = labels.values.copy()
        rng = np.random.default_rng(0)
        cnt = 0
        for _ in range(10000):
            rng.shuffle(labs)
            perm = np.zeros((len(cats.categories), 2))
            for i in range(len(cats.categories)):
                mask = codes == i
                perm[i, 0] = np.sum(labs[mask] == 'Combination')
                perm[i, 1] = np.sum(labs[mask] == 'Monotherapy')
            val = chi2_contingency(perm, correction=False)[0]
            if val >= obs:
                cnt += 1
        return cnt / 10000
    return chi2_contingency(table, correction=False)[1]


def p_cont(series: pd.Series, labels: pd.Series) -> float:
    g1 = series[labels == 'Combination'].dropna()
    g2 = series[labels == 'Monotherapy'].dropna()
    if g1.empty or g2.empty:
        return np.nan
    n1 = len(g1)
    n2 = len(g2)
    normal = n1 >= 30 and n2 >= 30 and shapiro(g1).pvalue > 0.05 and shapiro(g2).pvalue > 0.05
    if normal:
        return ttest_ind(g1, g2, equal_var=False).pvalue
    return mannwhitneyu(g1, g2, alternative='two-sided').pvalue


def fmt_pct(n: int, d: int) -> str:
    return f'{n} ({n / d * 100:.1f}%)' if d else '0 (0.0%)'


def fmt_iqr(series: pd.Series) -> str:
    return f'{int(series.median())} ({int(series.quantile(0.25))}-{int(series.quantile(0.75))})'


def fmt_range(series: pd.Series) -> str:
    return f'{int(series.min())}-{int(series.max())}'


def build_tables():
    total = load('Total')
    mono = load('Monotherapy')
    combo = load('Combination')
    labels = pd.Series(['Combination'] * len(combo) + ['Monotherapy'] * len(mono))
    days_t, courses_t = parse_ext(total[COL_EXT])
    days_m, courses_m = parse_ext(mono[COL_EXT])
    days_c, courses_c = parse_ext(combo[COL_EXT])
    t_x_rows = [
        'First-line therapy\u00b9, n (%)',
        'Remdesivir',
        'Molnupiravir',
        'Standard 5-day NMV-r',
        'Other antivirals',
        'Last line therapy\u00b2, n (%)',
        'Combination therapy',
        'Monotherapy',
        'Treatment courses, n (%)',
        'Single prolonged course',
        'Multiple courses',
        'Duration',
        'Median duration, days (IQR)',
        'Duration range, days',
    ]
    t_x = pd.DataFrame(index=t_x_rows, columns=[
        'Primary Cohort (n=104)',
        'Subgroup monotherapy (n=33)',
        'Subgroup combination (n=57)',
        'p-value',
    ])

    def add_rate(row, ser_total, ser_mono, ser_combo):
        t_x.at[row, 'Primary Cohort (n=104)'] = fmt_pct(int(ser_total.sum()), len(total))
        t_x.at[row, 'Subgroup monotherapy (n=33)'] = fmt_pct(int(ser_mono.sum()), len(mono))
        t_x.at[row, 'Subgroup combination (n=57)'] = fmt_pct(int(ser_combo.sum()), len(combo))
        t_x.at[row, 'p-value'] = f"{p_cat(pd.concat([ser_combo, ser_mono]), labels):.3f}" if ser_total.sum() else ''

    remd_t = total[COL_OTHER].fillna('').str.contains('RDV', case=False)
    remd_m = mono[COL_OTHER].fillna('').str.contains('RDV', case=False)
    remd_c = combo[COL_OTHER].fillna('').str.contains('RDV', case=False)
    add_rate('Remdesivir', remd_t, remd_m, remd_c)
    moln_t = total[COL_OTHER].fillna('').str.contains('MPV', case=False)
    moln_m = mono[COL_OTHER].fillna('').str.contains('MPV', case=False)
    moln_c = combo[COL_OTHER].fillna('').str.contains('MPV', case=False)
    add_rate('Molnupiravir', moln_t, moln_m, moln_c)
    nmv_t = pd.to_numeric(total[COL_NMV_STD], errors='coerce') > 0
    nmv_m = pd.to_numeric(mono[COL_NMV_STD], errors='coerce') > 0
    nmv_c = pd.to_numeric(combo[COL_NMV_STD], errors='coerce') > 0
    add_rate('Standard 5-day NMV-r', nmv_t, nmv_m, nmv_c)
    oth_t = (~total[COL_OTHER].fillna('').str.lower().str.contains('none')) & ~remd_t & ~moln_t
    oth_m = (~mono[COL_OTHER].fillna('').str.lower().str.contains('none')) & ~remd_m & ~moln_m
    oth_c = (~combo[COL_OTHER].fillna('').str.lower().str.contains('none')) & ~remd_c & ~moln_c
    add_rate('Other antivirals', oth_t, oth_m, oth_c)
    t_x.loc['First-line therapy\u00b9, n (%)'] = ''
    mon_t = total[COL_THERAPY].str.startswith('m', na=False)
    com_t = total[COL_THERAPY].str.startswith('c', na=False)
    t_x.at['Combination therapy', 'Primary Cohort (n=104)'] = fmt_pct(int(com_t.sum()), len(total))
    t_x.at['Monotherapy', 'Primary Cohort (n=104)'] = fmt_pct(int(mon_t.sum()), len(total))
    t_x.at['Subgroup monotherapy (n=33)'] = ['', fmt_pct(len(mono), len(mono)), '', '']
    t_x.at['Subgroup combination (n=57)'] = ['', '', fmt_pct(len(combo), len(combo)), '']
    t_x.at['Last line therapy\u00b2, n (%)'] = ''
    single_t = courses_t == 1
    single_m = courses_m == 1
    single_c = courses_c == 1
    add_rate('Single prolonged course', single_t, single_m, single_c)
    multi_t = courses_t > 1
    multi_m = courses_m > 1
    multi_c = courses_c > 1
    add_rate('Multiple courses', multi_t, multi_m, multi_c)
    t_x.loc['Treatment courses, n (%)'] = ''
    t_x.at['Median duration, days (IQR)', 'Primary Cohort (n=104)'] = fmt_iqr(days_t)
    t_x.at['Median duration, days (IQR)', 'Subgroup monotherapy (n=33)'] = fmt_iqr(days_m)
    t_x.at['Median duration, days (IQR)', 'Subgroup combination (n=57)'] = fmt_iqr(days_c)
    t_x.at['Duration range, days', 'Primary Cohort (n=104)'] = fmt_range(days_t)
    t_x.at['Duration range, days', 'Subgroup monotherapy (n=33)'] = fmt_range(days_m)
    t_x.at['Duration range, days', 'Subgroup combination (n=57)'] = fmt_range(days_c)
    t_x.loc['Duration'] = ''
    t_x.at['Median duration, days (IQR)', 'p-value'] = f"{p_cont(pd.concat([days_c, days_m]), labels):.3f}"
    t_y_rows = [
        'Age, median (IQR)',
        'Female sex, n (%)',
        'Underlying conditions, n (%)',
        'Hematological malignancy',
        'Autoimmune',
        'Transplantation',
        'Immunosuppressive treatment, n (%)',
        'Anti-CD20',
        'CAR-T',
        'HSCT',
        'None',
        'Glucocorticoid use, n (%)',
        'SARS-CoV-2 vaccination, n (%)',
        'Vaccination doses, n (range)',
        'Thoracic CT changes, n (%)',
        'Treatment setting\u00b9, n (%)',
        'Hospital',
        'Outpatient',
    ]
    t_y = pd.DataFrame(index=t_y_rows, columns=[
        'Primary Cohort (n=104)',
        'Subgroup monotherapy (n=33)',
        'Subgroup combination (n=57)',
        'p-value',
    ])
    t_y.loc['Underlying conditions, n (%)'] = ''
    t_y.loc['Immunosuppressive treatment, n (%)'] = ''
    t_y.loc['Treatment setting\u00b9, n (%)'] = ''
    age_t = total[COL_AGE]
    age_m = mono[COL_AGE]
    age_c = combo[COL_AGE]
    t_y.at['Age, median (IQR)', 'Primary Cohort (n=104)'] = fmt_iqr(age_t)
    t_y.at['Age, median (IQR)', 'Subgroup monotherapy (n=33)'] = fmt_iqr(age_m)
    t_y.at['Age, median (IQR)', 'Subgroup combination (n=57)'] = fmt_iqr(age_c)
    t_y.at['Age, median (IQR)', 'p-value'] = f"{p_cont(pd.concat([age_c, age_m]), labels):.3f}"
    female_t = total[COL_SEX].str.lower().str.startswith('f')
    female_m = mono[COL_SEX].str.lower().str.startswith('f')
    female_c = combo[COL_SEX].str.lower().str.startswith('f')

    def add_y(row, ser_total, ser_mono, ser_combo):
        t_y.at[row, 'Primary Cohort (n=104)'] = fmt_pct(int(ser_total.sum()), len(total))
        t_y.at[row, 'Subgroup monotherapy (n=33)'] = fmt_pct(int(ser_mono.sum()), len(mono))
        t_y.at[row, 'Subgroup combination (n=57)'] = fmt_pct(int(ser_combo.sum()), len(combo))
        t_y.at[row, 'p-value'] = f"{p_cat(pd.concat([ser_combo, ser_mono]), labels):.3f}" if ser_total.sum() else ''

    add_y('Female sex, n (%)', female_t, female_m, female_c)
    dis_t = total[COL_DIS].map(group_disease)
    dis_m = mono[COL_DIS].map(group_disease)
    dis_c = combo[COL_DIS].map(group_disease)
    for cat in ['Hematological malignancy', 'Autoimmune', 'Transplantation']:
        add_y(cat, dis_t == cat, dis_m == cat, dis_c == cat)
    imm_t = total[COL_BASE].map(group_immuno)
    imm_m = mono[COL_BASE].map(group_immuno)
    imm_c = combo[COL_BASE].map(group_immuno)
    for cat in ['Anti-CD20', 'CAR-T', 'HSCT', 'None']:
        add_y(cat, imm_t == cat, imm_m == cat, imm_c == cat)
    gc_t = total[COL_GC].map(flag_gc) == 'Yes'
    gc_m = mono[COL_GC].map(flag_gc) == 'Yes'
    gc_c = combo[COL_GC].map(flag_gc) == 'Yes'
    add_y('Glucocorticoid use, n (%)', gc_t, gc_m, gc_c)
    vacc_t = total[COL_VACC].map(lambda x: parse_vacc(x)[0]) == 'Yes'
    vacc_m = mono[COL_VACC].map(lambda x: parse_vacc(x)[0]) == 'Yes'
    vacc_c = combo[COL_VACC].map(lambda x: parse_vacc(x)[0]) == 'Yes'
    add_y('SARS-CoV-2 vaccination, n (%)', vacc_t, vacc_m, vacc_c)
    doses_t = total[COL_VACC].map(lambda x: parse_vacc(x)[1])
    doses_m = mono[COL_VACC].map(lambda x: parse_vacc(x)[1])
    doses_c = combo[COL_VACC].map(lambda x: parse_vacc(x)[1])
    t_y.at['Vaccination doses, n (range)', 'Primary Cohort (n=104)'] = fmt_range(doses_t.dropna())
    t_y.at['Vaccination doses, n (range)', 'Subgroup monotherapy (n=33)'] = fmt_range(doses_m.dropna())
    t_y.at['Vaccination doses, n (range)', 'Subgroup combination (n=57)'] = fmt_range(doses_c.dropna())
    t_y.at['Vaccination doses, n (range)', 'p-value'] = f"{p_cont(pd.concat([doses_c, doses_m]), labels):.3f}"
    ct_t = total[COL_CT].map(group_ct) == 'Yes'
    ct_m = mono[COL_CT].map(group_ct) == 'Yes'
    ct_c = combo[COL_CT].map(group_ct) == 'Yes'
    add_y('Thoracic CT changes, n (%)', ct_t, ct_m, ct_c)
    hosp_t = total[COL_HOSP].str.lower().str.startswith('y')
    hosp_m = mono[COL_HOSP].str.lower().str.startswith('y')
    hosp_c = combo[COL_HOSP].str.lower().str.startswith('y')
    add_y('Hospital', hosp_t, hosp_m, hosp_c)
    out_t = total[COL_HOSP].str.lower().str.startswith('n')
    out_m = mono[COL_HOSP].str.lower().str.startswith('n')
    out_c = combo[COL_HOSP].str.lower().str.startswith('n')
    add_y('Outpatient', out_t, out_m, out_c)
    return t_x, t_y


if __name__ == '__main__':
    tab_x, tab_y = build_tables()
    print('Table X. Treatment Approach.')
    print(tab_x.to_string())
    print('* NMV-r, nirmatrelvir-ritonavir.')
    print(
        "* \u00b9 Any treatment administered prior to extended nirmatrelvir-ritonavir, "
        "including standard 5-day Paxlovid courses with or without other antivirals."
    )
    print(
        "* \u00b2 Extended nirmatrelvir-ritonavir regimens (with or without concurrent antivirals) "
        "when no subsequent antiviral therapy was administered."
    )
    print('Table Y. Demographics and Clinical Characteristics.')
    print(tab_y.to_string())
    print('* NMV-r, nirmatrelvir-ritonavir.')
    print('* \u00b9 Treatment setting where prolonged NMV-r was administered.')
