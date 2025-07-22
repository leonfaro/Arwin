import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu, shapiro, ttest_ind
import re

FILES = {"mono": "Monotherapy.xlsx", "comb": "Combination.xlsx"}
DF_mono = pd.read_excel(FILES["mono"])
DF_comb = pd.read_excel(FILES["comb"])

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

total = pd.read_excel('Total.xlsx')
mono = pd.read_excel('Monotherapy.xlsx')
combo = pd.read_excel('Combination.xlsx')


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
    dose = float(m.iloc[0]) if m.notna().any() else np.nan
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


def chi_or_fisher(a11, a12, a21, a22):
    exp = chi2_contingency([[a11, a12], [a21, a22]])[3]
    if (exp < 5).any():
        return fisher_exact([[a11, a12], [a21, a22]])[1]
    return chi2_contingency([[a11, a12], [a21, a22]])[1]


def cont_test(v1, v2):
    if shapiro(v1).pvalue >= 0.05 and shapiro(v2).pvalue >= 0.05:
        return ttest_ind(v1, v2, equal_var=False).pvalue
    return mannwhitneyu(v1, v2).pvalue


def fmt_p(p):
    if p < 0.001:
        return "<0.001"
    return f"{round(p, 3):.3f}"


def fmt_pct(n: int, d: int) -> str:
    return f'{n} ({n / d * 100:.1f}%)' if d else '0 (0.0%)'


def fmt_iqr(series: pd.Series) -> str:
    return f'{int(series.median())} ({int(series.quantile(0.25))}-{int(series.quantile(0.75))})'


def fmt_range(series: pd.Series) -> str:
    return f'{int(series.min())}-{int(series.max())}'


def build_tables():
    days_t, courses_t = parse_ext(total[COL_EXT])
    days_m, courses_m = parse_ext(mono[COL_EXT])
    days_c, courses_c = parse_ext(combo[COL_EXT])
    t_x_index = pd.MultiIndex.from_tuples(
        [
            ('N=', ''),
            ('First-line therapy\u00b9, n (%)', ''),
            ('First-line therapy\u00b9, n (%)', 'Remdesivir'),
            ('First-line therapy\u00b9, n (%)', 'Molnupiravir'),
            (
                'First-line therapy\u00b9, n (%)',
                'Standard 5-day NMV-r',
            ),
            ('First-line therapy\u00b9, n (%)', 'Other antivirals'),
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
    t_x = pd.DataFrame(index=t_x_index, columns=[
        'Primary Cohort (n=104)',
        'Subgroup monotherapy (n=33)',
        'Subgroup combination (n=57)',
        'p-value',
    ])
    t_x.at[('N=', ''), 'Primary Cohort (n=104)'] = len(total)
    t_x.at[('N=', ''), 'Subgroup monotherapy (n=33)'] = len(mono)
    t_x.at[('N=', ''), 'Subgroup combination (n=57)'] = len(combo)
    t_x.at[('N=', ''), 'p-value'] = ''

    def add_rate(row, ser_total, ser_mono, ser_combo):
        t_x.at[row, 'Primary Cohort (n=104)'] = fmt_pct(int(ser_total.sum()), len(total))
        t_x.at[row, 'Subgroup monotherapy (n=33)'] = fmt_pct(int(ser_mono.sum()), len(mono))
        t_x.at[row, 'Subgroup combination (n=57)'] = fmt_pct(int(ser_combo.sum()), len(combo))
        if ser_total.sum():
            a11 = int(ser_combo.sum())
            a12 = len(ser_combo) - a11
            a21 = int(ser_mono.sum())
            a22 = len(ser_mono) - a21
            p = chi_or_fisher(a11, a12, a21, a22)
            t_x.at[row, 'p-value'] = fmt_p(p)
        else:
            t_x.at[row, 'p-value'] = ''

    drug_map = {
        'rdv': 'Remdesivir',
        'remdesivir': 'Remdesivir',
        'mpv': 'Molnupiravir',
        'molnupiravir': 'Molnupiravir',
    }

    def classify(row):
        if pd.to_numeric(row[COL_NMV_STD], errors='coerce') >= 1:
            return 'Standard 5-day NMV-r'
        txt = str(row[COL_OTHER]).lower()
        for k, d in drug_map.items():
            if k in txt:
                return d
        return 'Other antivirals'

    cat_t = total.apply(classify, axis=1)
    cat_m = mono.apply(classify, axis=1)
    cat_c = combo.apply(classify, axis=1)
    for c in ['Remdesivir', 'Molnupiravir', 'Standard 5-day NMV-r', 'Other antivirals']:
        add_rate(('First-line therapy\u00b9, n (%)', c), cat_t == c, cat_m == c, cat_c == c)
    t_x.loc[('First-line therapy\u00b9, n (%)', '')] = ''
    com_flag_t = total[COL_THERAPY].str.startswith('c', na=False)
    mono_flag_t = total[COL_THERAPY].str.startswith('m', na=False)
    idx = ('Last line therapy\u00b2, n (%)', 'Combination therapy')
    t_x.at[idx, 'Primary Cohort (n=104)'] = fmt_pct(int(com_flag_t.sum()), len(total))
    t_x.at[idx, 'Subgroup monotherapy (n=33)'] = fmt_pct(0, len(mono))
    t_x.at[idx, 'Subgroup combination (n=57)'] = fmt_pct(len(combo), len(combo))
    p_last = chi_or_fisher(len(combo), 0, 0, len(mono))
    t_x.at[idx, 'p-value'] = fmt_p(p_last)
    idx = ('Last line therapy\u00b2, n (%)', 'Monotherapy')
    t_x.at[idx, 'Primary Cohort (n=104)'] = fmt_pct(int(mono_flag_t.sum()), len(total))
    t_x.at[idx, 'Subgroup monotherapy (n=33)'] = fmt_pct(len(mono), len(mono))
    t_x.at[idx, 'Subgroup combination (n=57)'] = fmt_pct(0, len(combo))
    t_x.at[idx, 'p-value'] = ''
    t_x.loc[('Last line therapy\u00b2, n (%)', '')] = ''
    single_t = courses_t == 1
    multi_t = courses_t > 1
    single_m = courses_m == 1
    multi_m = courses_m > 1
    single_c = courses_c == 1
    multi_c = courses_c > 1
    row = ('Treatment courses, n (%)', 'Single prolonged course')
    t_x.at[row, 'Primary Cohort (n=104)'] = fmt_pct(int(single_t.sum()), len(total))
    t_x.at[row, 'Subgroup monotherapy (n=33)'] = fmt_pct(int(single_m.sum()), len(mono))
    t_x.at[row, 'Subgroup combination (n=57)'] = fmt_pct(int(single_c.sum()), len(combo))
    row = ('Treatment courses, n (%)', 'Multiple courses')
    t_x.at[row, 'Primary Cohort (n=104)'] = fmt_pct(int(multi_t.sum()), len(total))
    t_x.at[row, 'Subgroup monotherapy (n=33)'] = fmt_pct(int(multi_m.sum()), len(mono))
    t_x.at[row, 'Subgroup combination (n=57)'] = fmt_pct(int(multi_c.sum()), len(combo))
    p_course = chi_or_fisher(int(single_c.sum()), int(multi_c.sum()), int(single_m.sum()), int(multi_m.sum()))
    t_x.at[('Treatment courses, n (%)', 'Single prolonged course'), 'p-value'] = fmt_p(p_course)
    t_x.at[('Treatment courses, n (%)', 'Multiple courses'), 'p-value'] = ''
    t_x.loc[('Treatment courses, n (%)', '')] = ''
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'Primary Cohort (n=104)'] = fmt_iqr(days_t)
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'Subgroup monotherapy (n=33)'] = fmt_iqr(days_m)
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'Subgroup combination (n=57)'] = fmt_iqr(days_c)
    t_x.at[('Duration', 'Duration range, days'), 'Primary Cohort (n=104)'] = fmt_range(days_t)
    t_x.at[('Duration', 'Duration range, days'), 'Subgroup monotherapy (n=33)'] = fmt_range(days_m)
    t_x.at[('Duration', 'Duration range, days'), 'Subgroup combination (n=57)'] = fmt_range(days_c)
    t_x.loc[('Duration', '')] = ''
    p_dur = cont_test(days_m.dropna(), days_c.dropna())
    t_x.at[('Duration', 'Median duration, days (IQR)'), 'p-value'] = fmt_p(p_dur)
    t_x.at[('Duration', 'Duration range, days'), 'p-value'] = fmt_p(p_dur)
    t_y_index = pd.MultiIndex.from_tuples(
        [
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
            ('Immunosuppressive treatment, n (%)', 'None'),
            ('Glucocorticoid use, n (%)', ''),
            ('SARS-CoV-2 vaccination, n (%)', ''),
            ('Vaccination doses, n (range)', ''),
            ('Thoracic CT changes, n (%)', ''),
            ('Treatment setting\u00b9, n (%)', ''),
            ('Treatment setting\u00b9, n (%)', 'Hospital'),
            ('Treatment setting\u00b9, n (%)', 'Outpatient'),
        ],
        names=['Category', 'Subcategory'],
    )
    t_y = pd.DataFrame(index=t_y_index, columns=[
        'Primary Cohort (n=104)',
        'Subgroup monotherapy (n=33)',
        'Subgroup combination (n=57)',
        'p-value',
    ])

    def age_fmt(s):
        return f"{int(s.median())} ({int(s.quantile(0.25))}\u2013{int(s.quantile(0.75))})"

    def n_pct(count, n):
        return f"{count} ({round(count/n*100)}%)"

    def cond(series, letter):
        return sum(letter in str(c).lower() for c in series)

    def immuno(x):
        s = str(x).lower()
        if any(k in s for k in ['rtx', 'obi', 'ocr', 'mos']):
            return 'Anti-CD20'
        if 'car' in s:
            return 'CAR-T'
        if 'hsct' in s:
            return 'HSCT'
        return 'None'
    res = {}
    for label, frame in {'Primary Cohort': total, 'Subgroup monotherapy': mono, 'Subgroup combination': combo}.items():
        n = len(frame)
        vacc_yes = frame[COL_VACC].astype(str).str.lower().str.startswith('y')
        doses = pd.to_numeric(frame.loc[vacc_yes, COL_VACC].str.extract(r"\((\d+)\)")[0], errors='coerce')
        out = {
            'Age': age_fmt(frame[COL_AGE]),
            'Female': n_pct((frame[COL_SEX].str.lower() == 'f').sum(), n),
            'Hematological malignancy': n_pct(cond(frame[COL_DIS], 'm'), n),
            'Autoimmune': n_pct(cond(frame[COL_DIS], 'a'), n),
            'Transplantation': n_pct(cond(frame[COL_DIS], 't'), n),
        }
        cats = frame[COL_BASE].map(immuno)
        out['Anti-CD20'] = n_pct((cats == 'Anti-CD20').sum(), n)
        out['CAR-T'] = n_pct((cats == 'CAR-T').sum(), n)
        out['HSCT'] = n_pct((cats == 'HSCT').sum(), n)
        out['None'] = n_pct((cats == 'None').sum(), n)
        out['Glucocorticoid use'] = n_pct((frame[COL_GC].str.lower() == 'y').sum(), n)
        out['Vaccinated'] = n_pct(vacc_yes.sum(), n)
        out['Vaccination doses'] = f"{int(doses.median())} ({int(doses.min())}\u2013{int(doses.max())})"
        out['CT changes'] = n_pct((frame[COL_CT].str.lower() == 'y').sum(), n)
        hosp = frame[COL_HOSP].str.lower()
        out['Hospital'] = n_pct((hosp == 'y').sum(), n)
        out['Outpatient'] = n_pct((hosp != 'y').sum(), n)
        res[label] = out
    for row, key in [
        (('Age, median (IQR)', ''), 'Age'),
        (('Female sex, n (%)', ''), 'Female'),
        (('Underlying conditions, n (%)', 'Hematological malignancy'), 'Hematological malignancy'),
        (('Underlying conditions, n (%)', 'Autoimmune'), 'Autoimmune'),
        (('Underlying conditions, n (%)', 'Transplantation'), 'Transplantation'),
        (('Immunosuppressive treatment, n (%)', 'Anti-CD20'), 'Anti-CD20'),
        (('Immunosuppressive treatment, n (%)', 'CAR-T'), 'CAR-T'),
        (('Immunosuppressive treatment, n (%)', 'HSCT'), 'HSCT'),
        (('Immunosuppressive treatment, n (%)', 'None'), 'None'),
        (('Glucocorticoid use, n (%)', ''), 'Glucocorticoid use'),
        (('SARS-CoV-2 vaccination, n (%)', ''), 'Vaccinated'),
        (('Vaccination doses, n (range)', ''), 'Vaccination doses'),
        (('Thoracic CT changes, n (%)', ''), 'CT changes'),
        (('Treatment setting\u00b9, n (%)', 'Hospital'), 'Hospital'),
        (('Treatment setting\u00b9, n (%)', 'Outpatient'), 'Outpatient'),
    ]:
        for col, lab in zip(t_y.columns[:-1], res.keys()):
            t_y.at[row, col] = res[lab][key]
    p_age = cont_test(DF_mono[COL_AGE].dropna(), DF_comb[COL_AGE].dropna())
    t_y.at[('Age, median (IQR)', ''), 'p-value'] = fmt_p(p_age)
    f_mono = DF_mono[COL_SEX].astype(str).str.lower().str.startswith('f')
    f_comb = DF_comb[COL_SEX].astype(str).str.lower().str.startswith('f')
    cmb_n = len(f_comb)
    mono_n = len(f_mono)
    p_fem = chi_or_fisher(int(f_comb.sum()), cmb_n - int(f_comb.sum()), int(f_mono.sum()), mono_n - int(f_mono.sum()))
    t_y.at[('Female sex, n (%)', ''), 'p-value'] = fmt_p(p_fem)
    for lab, letter in [('Hematological malignancy', 'm'), ('Autoimmune', 'a'), ('Transplantation', 't')]:
        m1 = DF_comb[COL_DIS].astype(str).str.lower().str.contains(letter)
        m2 = DF_mono[COL_DIS].astype(str).str.lower().str.contains(letter)
        c1n = len(m1)
        c2n = len(m2)
        val = chi_or_fisher(int(m1.sum()), c1n - int(m1.sum()), int(m2.sum()), c2n - int(m2.sum()))
        t_y.at[('Underlying conditions, n (%)', lab), 'p-value'] = fmt_p(val)
    ic_mono = DF_mono[COL_BASE].map(group_immuno)
    ic_comb = DF_comb[COL_BASE].map(group_immuno)
    for cat in ['Anti-CD20', 'CAR-T', 'HSCT', 'None']:
        c1 = ic_comb == cat
        c2 = ic_mono == cat
        c1n = len(c1)
        c2n = len(c2)
        val = chi_or_fisher(int(c1.sum()), c1n - int(c1.sum()), int(c2.sum()), c2n - int(c2.sum()))
        t_y.at[('Immunosuppressive treatment, n (%)', cat), 'p-value'] = fmt_p(val)
    gc_mono = DF_mono[COL_GC].astype(str).str.lower().str.startswith('y')
    gc_comb = DF_comb[COL_GC].astype(str).str.lower().str.startswith('y')
    c1n = len(gc_comb)
    c2n = len(gc_mono)
    p_gc = chi_or_fisher(int(gc_comb.sum()), c1n - int(gc_comb.sum()), int(gc_mono.sum()), c2n - int(gc_mono.sum()))
    t_y.at[('Glucocorticoid use, n (%)', ''), 'p-value'] = fmt_p(p_gc)
    v_mono = DF_mono[COL_VACC].astype(str).str.lower().str.startswith('y')
    v_comb = DF_comb[COL_VACC].astype(str).str.lower().str.startswith('y')
    c1n = len(v_comb)
    c2n = len(v_mono)
    p_vacc = chi_or_fisher(int(v_comb.sum()), c1n - int(v_comb.sum()), int(v_mono.sum()), c2n - int(v_mono.sum()))
    t_y.at[('SARS-CoV-2 vaccination, n (%)', ''), 'p-value'] = fmt_p(p_vacc)
    d_mono = DF_mono[COL_VACC].map(lambda x: parse_vacc(x)[1])
    d_comb = DF_comb[COL_VACC].map(lambda x: parse_vacc(x)[1])
    p_dose = cont_test(d_mono.dropna(), d_comb.dropna())
    t_y.at[('Vaccination doses, n (range)', ''), 'p-value'] = fmt_p(p_dose)
    ct_mono = DF_mono[COL_CT].astype(str).str.lower().str.startswith('y')
    ct_comb = DF_comb[COL_CT].astype(str).str.lower().str.startswith('y')
    c1n = len(ct_comb)
    c2n = len(ct_mono)
    p_ct = chi_or_fisher(int(ct_comb.sum()), c1n - int(ct_comb.sum()), int(ct_mono.sum()), c2n - int(ct_mono.sum()))
    t_y.at[('Thoracic CT changes, n (%)', ''), 'p-value'] = fmt_p(p_ct)
    h_mono = DF_mono[COL_HOSP].astype(str).str.lower().str.startswith('y')
    h_comb = DF_comb[COL_HOSP].astype(str).str.lower().str.startswith('y')
    c1n = len(h_comb)
    c2n = len(h_mono)
    p_hosp = chi_or_fisher(int(h_comb.sum()), c1n - int(h_comb.sum()), int(h_mono.sum()), c2n - int(h_mono.sum()))
    t_y.at[('Treatment setting\u00b9, n (%)', 'Hospital'), 'p-value'] = fmt_p(p_hosp)
    t_y.at[('Treatment setting\u00b9, n (%)', 'Outpatient'), 'p-value'] = fmt_p(p_hosp)
    t_y.loc[('Underlying conditions, n (%)', '')] = ''
    t_y.loc[('Immunosuppressive treatment, n (%)', '')] = ''
    t_y.loc[('Treatment setting\u00b9, n (%)', '')] = ''
    return t_x, t_y


def build_table():
    def load_file(label, frame):
        df_tmp = frame.copy()
        df_tmp['group'] = label
        df_tmp['source_sheet'] = label
        col = None
        for c in df_tmp.columns:
            if str(c).lower().startswith('2nd line treatment form of therapy'):
                col = c
                break
        if col is not None:
            df_tmp['therapy'] = (
                df_tmp[col]
                .str.lower()
                .str[0]
                .map({'c': 'Combination', 'm': 'Monotherapy'})
                .fillna('Unknown')
            )
        else:
            df_tmp['therapy'] = label
        return df_tmp

    df_total = load_file('Total', total)
    df_combo = load_file('Combination', combo)
    df_mono = load_file('Monotherapy', mono)
    df = df_total.copy()

    def find_col(df_, *keywords):
        kws = [k.lower() for k in keywords]
        for c in df_.columns:
            s = str(c).lower()
            if all(k in s for k in kws):
                return c
        raise KeyError(','.join(keywords))

    col_therapy = None
    for c in df.columns:
        if str(c).lower().startswith('2nd line treatment form of therapy'):
            col_therapy = c
            break
    if col_therapy is not None:
        therapy = df[col_therapy].str.lower().str[0].map({'c': 'Combination', 'm': 'Monotherapy'})
        therapy = therapy.fillna('Unknown')
    else:
        def infer(x):
            s = str(x)
            if 'combo' in s.lower():
                return 'Combination'
            if 'mono' in s.lower():
                return 'Monotherapy'
            return np.nan

        therapy = df['source_sheet'].map(infer).fillna('Unknown')
        df[col_therapy] = ''
    df['therapy'] = therapy

    col_sex = find_col(df, 'sex')
    col_age = find_col(df, 'age')
    col_disease = find_col(df, 'baseline disease cohort')
    col_base = find_col(df, 'baseline therapy')
    col_vacc = find_col(df, 'vaccination')
    col_gen = find_col(df, 'sars-cov-2', 'genotype')
    col_ct = find_col(df, 'ct', 'lung')
    col_rep = find_col(df, 'replication')
    col_gc = find_col(df, 'glucocorticosteroid')
    col_adv = find_col(df, 'any adverse events')
    col_adv_type = find_col(df, 'type of adverse')
    col_surv = find_col(df, 'survival outcome')

    mandatory = [
        col_sex,
        col_age,
        col_disease,
        col_base,
        col_vacc,
        col_gen,
        col_ct,
        col_rep,
        col_gc,
        col_adv,
        col_adv_type,
        col_surv,
    ]
    missing = [c for c in mandatory if c not in df.columns]
    print(len(df), len(df.columns), df['therapy'].value_counts().to_dict(), missing)
    if missing:
        raise SystemExit('missing columns')

    def group_disease(x):
        if not isinstance(x, str):
            return 'Unknown'
        s = x.upper()
        a = 'AUTO' in s
        m = 'MALIGN' in s
        t = 'TRANSPLANT' in s
        if sum([a, m, t]) > 1:
            return 'Mixed'
        if a:
            return 'Autoimmune disease'
        if m:
            return 'Haematological malignancy'
        if t:
            return 'Transplantation'
        return 'Unknown'

    def group_immuno_detail(x):
        if not isinstance(x, str) or not x.strip():
            return 'None'
        s = x.lower()
        if any(k in s for k in ('ritux', 'obinu', 'ocrel', 'mosune', 'cd-20')):
            return 'Anti-CD-20'
        if 'none' in s or 'no is' in s:
            return 'None'
        return 'Other'

    def is_female(x):
        s = str(x).lower().strip()
        if s in {'f', 'female', 'w', 'weiblich', '1'}:
            return True
        if s in {'m', 'male', '0', 'mann', 'männlich'}:
            return False
        return np.nan

    def flag_gc(x):
        if not isinstance(x, str):
            return 'Unknown'
        s = x.lower().strip()
        if s.startswith('y'):
            return 'Yes'
        if s.startswith('n'):
            return 'No'
        if not s:
            return 'Unknown'
        if any(k in s for k in ('pdn', 'pred', 'dxa', 'dexa', 'meth')):
            return 'Yes'
        return 'Yes'

    def parse_vacc(x):
        if not isinstance(x, str):
            return ('Unknown', np.nan)
        s = x.lower().strip()
        m = re.search(r'(\d+)', s)
        dose = float(m.group(1)) if m else 0.0
        if s.startswith('n') or dose == 0:
            return ('No', dose)
        if dose >= 1:
            return ('Yes', dose)
        return ('Unknown', np.nan)

    def group_dose(x):
        if pd.isna(x):
            return np.nan
        if x >= 5:
            return '≥5'
        if x >= 3:
            return '3-4'
        if x >= 1:
            return '1-2'
        return '0'

    def group_ct(x):
        if not isinstance(x, str):
            return 'Unknown'
        s = x.lower().strip()
        if re.search(r'y|yes|opa|ggo|infilt', s):
            return 'Yes'
        if re.search(r'n|no|normal', s):
            return 'No'
        return 'Unknown'

    def parse_rep(x):
        if isinstance(x, (int, float)) and not pd.isna(x):
            return float(x)
        if not isinstance(x, str):
            return np.nan
        m = re.search(r'(\d+)', x)
        return float(m.group(1)) if m else np.nan

    def group_variant(x):
        if not isinstance(x, str):
            return 'Unknown'
        s = x.upper().strip()
        if re.search(r'BQ\.?1', s):
            return 'BQ.1.x'
        if re.search(r'BA\.?5', s):
            return 'BA.5.x'
        if re.search(r'BA\.?4', s):
            return 'BA.4.x'
        if re.search(r'BA\.?2', s):
            return 'BA.2.x'
        if re.search(r'BA\.?1', s):
            return 'BA.1.x'
        if re.search(r'XBB', s):
            return 'XBB.x'
        if re.search(r'JN', s):
            return 'JN.x'
        return 'Other'

    def flag_survival(x):
        if not isinstance(x, str):
            return 'Unknown'
        s = x.lower().strip()
        if re.search(r'^(alive|yes|1)', s):
            return 'Yes'
        if re.search(r'^(dead|no|0)', s):
            return 'No'
        return 'Unknown'

    def group_adv(a, t):
        a_s = str(a).lower().strip()
        t_s = str(t).lower()
        if a_s.startswith('y'):
            if 'thrombocyt' in t_s:
                return 'Thrombocytopenia'
            return 'Other'
        if a_s.startswith('n') or a_s in {'none', ''}:
            return 'None'
        return 'Unknown'

    def transform(d):
        d['disease'] = d[col_disease].map(group_disease)
        d['immuno_detail'] = d[col_base].map(group_immuno_detail)
        d['immuno3'] = d['immuno_detail'].map(
            lambda x: 'Anti-CD-20' if x == 'Anti-CD-20' else ('None' if x == 'None' else 'Other')
        )
        d['gc'] = d[col_gc].map(flag_gc)
        vacc = d[col_vacc].map(parse_vacc)
        d['vacc'] = vacc.map(lambda x: x[0])
        d['doses'] = vacc.map(lambda x: x[1])
        d['dose_group'] = d['doses'].map(group_dose)
        d['ct'] = d[col_ct].map(group_ct)
        d['rep'] = d[col_rep].map(parse_rep)
        d['variant'] = d[col_gen].map(group_variant)
        d['prolonged'] = d['rep'].map(lambda x: np.nan if pd.isna(x) else x >= 14)
        d['survival'] = d[col_surv].map(flag_survival)
        d['adverse'] = d.apply(lambda r: group_adv(r[col_adv], r[col_adv_type]), axis=1)
        return d

    df_total = transform(df_total)
    df_combo = transform(df_combo)
    df_mono = transform(df_mono)
    group_map = {'Total': df_total, 'Combination': df_combo, 'Monotherapy': df_mono}
    df = df_total

    def fmt_num(x, typ):
        if typ == 'mean':
            return f'{x.mean():.1f} ± {x.std():.1f}'
        return f'{int(x.median())} ({int(x.quantile(0.25))}-{int(x.quantile(0.75))})'

    def fmt_count(mask, denom=None):
        n = mask.sum()
        d = len(mask) if denom is None else denom
        if d == 0:
            return '0 (0.0%)'
        return f'{n} ({n / d * 100:.1f}%)'

    def unique_order(seq, order):
        return [i for i in order if i in seq]

    rows = ['N=', 'Age', 'Sex (female)', 'Disease group']
    disease_order = ['Haematological malignancy', 'Autoimmune disease', 'Transplantation', 'Mixed']
    rows += [f'  *{i}*' for i in unique_order(df['disease'].unique(), disease_order)]
    rows += ['Immunosuppressive treatment']
    immuno_order = ['Anti-CD-20', 'Other', 'None']
    rows += [f'  *{i}*' for i in unique_order(df['immuno_detail'].unique(), immuno_order)]
    rows += ['Glucocorticoid use', 'SARS-CoV-2 Vaccination', 'Number of vaccine doses']
    dose_order = ['0', '1-2', '3-4', '≥5']
    rows += [f'  *{i}*' for i in unique_order(df['dose_group'].dropna().unique(), dose_order)]
    rows += ['Thoracic CT changes', 'Duration of SARS-CoV-2 replication (days)', 'SARS-CoV-2 genotype']
    var_order = ['BA.1.x', 'BA.2.x', 'BA.4.x', 'BA.5.x', 'BQ.1.x', 'XBB.x', 'JN.x', 'Other']
    rows += [f'  *{i}*' for i in unique_order(df['variant'].unique(), var_order)]
    rows += ['Prolonged viral shedding (≥14 days)', 'Survival', 'Adverse events']
    ae_order = ['None', 'Thrombocytopenia', 'Other']
    rows += [f'  *{i}*' for i in unique_order(df['adverse'].unique(), ae_order)]

    groups = ['Total', 'Combination', 'Monotherapy']
    cols = groups
    out = pd.DataFrame(index=rows, columns=cols)
    out.loc['N=', 'Total'] = len(df_total)
    out.loc['N=', 'Combination'] = len(df_combo)
    out.loc['N=', 'Monotherapy'] = len(df_mono)

    for g in groups:
        d = group_map[g]
        out.at['Age', g] = fmt_num(d[col_age], 'median')

    female = df[col_sex].map(is_female)
    for g in groups:
        d = group_map[g]
        out.at['Sex (female)', g] = fmt_count(female.loc[d.index].fillna(False))

    for g in groups:
        d = group_map[g]
        for cat in unique_order(df['disease'].unique(), disease_order):
            out.at[f'  *{cat}*', g] = fmt_count(d['disease'] == cat)
    out.at['Disease group', 'Total'] = ''
    out.at['Disease group', 'Combination'] = ''
    out.at['Disease group', 'Monotherapy'] = ''

    for g in groups:
        d = group_map[g]
        for cat in unique_order(df['immuno_detail'].unique(), immuno_order):
            out.at[f'  *{cat}*', g] = fmt_count(d['immuno_detail'] == cat)
    out.at['Immunosuppressive treatment', 'Total'] = ''
    out.at['Immunosuppressive treatment', 'Combination'] = ''
    out.at['Immunosuppressive treatment', 'Monotherapy'] = ''

    for g in groups:
        d = group_map[g]
        out.at['Glucocorticoid use', g] = fmt_count(d['gc'] == 'Yes')

    for g in groups:
        d = group_map[g]
        out.at['SARS-CoV-2 Vaccination', g] = fmt_count(d['vacc'] == 'Yes')
    for g in groups:
        out.at['Number of vaccine doses', g] = ''
    for g in groups:
        d = group_map[g]
        for cat in unique_order(df['dose_group'].dropna().unique(), dose_order):
            out.at[f'  *{cat}*', g] = fmt_count(d['dose_group'] == cat)
    for g in groups:
        d = group_map[g]
        out.at['Thoracic CT changes', g] = fmt_count(d['ct'] == 'Yes')

    mode_rep = 'median'
    for g in groups:
        d = group_map[g]
        out.at['Duration of SARS-CoV-2 replication (days)', g] = fmt_num(d['rep'], mode_rep)

    for g in groups:
        d = group_map[g]
        for cat in unique_order(df['variant'].unique(), var_order):
            out.at[f'  *{cat}*', g] = fmt_count(d['variant'] == cat)
    out.at['SARS-CoV-2 genotype', 'Total'] = ''
    out.at['SARS-CoV-2 genotype', 'Combination'] = ''
    out.at['SARS-CoV-2 genotype', 'Monotherapy'] = ''

    for g in groups:
        d = group_map[g]
        out.at['Prolonged viral shedding (≥14 days)', g] = fmt_count(d['prolonged'])

    for g in groups:
        d = group_map[g]
        out.at['Survival', g] = fmt_count(d['survival'] == 'Yes')

    for g in groups:
        d = group_map[g]
        for cat in unique_order(df['adverse'].unique(), ae_order):
            name = 'None (AE)' if cat == 'None' else cat
            out.at[f'  *{name}*', g] = fmt_count(d['adverse'] == cat)
    out.at['Adverse events', 'Total'] = ''
    out.at['Adverse events', 'Combination'] = ''
    out.at['Adverse events', 'Monotherapy'] = ''
    return out


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
    tab_z = build_table()
    print('Table Z')
    print(tab_z.fillna(''))
    print('Anti-CD-20 umfasst Rituximab, Obinutuzumab, Ocrelizumab, Mosunetuzumab.')
