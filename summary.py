import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu, shapiro, ttest_ind
from statsmodels.stats.multitest import multipletests
import re

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


def p_cat(series: pd.Series, labels: pd.Series) -> float:
    ser = pd.Series(series).reset_index(drop=True)
    lab = pd.Series(labels).reset_index(drop=True)
    table = pd.crosstab(ser, lab)
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
    labels = pd.Series(['Combination'] * len(combo) + ['Monotherapy'] * len(mono))
    days_t, courses_t = parse_ext(total[COL_EXT])
    days_m, courses_m = parse_ext(mono[COL_EXT])
    days_c, courses_c = parse_ext(combo[COL_EXT])
    t_x_rows = [
        'N=',
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
    t_x.at['N=', 'Primary Cohort (n=104)'] = len(total)
    t_x.at['N=', 'Subgroup monotherapy (n=33)'] = len(mono)
    t_x.at['N=', 'Subgroup combination (n=57)'] = len(combo)
    t_x.at['N=', 'p-value'] = ''

    def add_rate(row, ser_total, ser_mono, ser_combo):
        t_x.at[row, 'Primary Cohort (n=104)'] = fmt_pct(int(ser_total.sum()), len(total))
        t_x.at[row, 'Subgroup monotherapy (n=33)'] = fmt_pct(int(ser_mono.sum()), len(mono))
        t_x.at[row, 'Subgroup combination (n=57)'] = fmt_pct(int(ser_combo.sum()), len(combo))
        if ser_total.sum():
            p = p_cat(pd.concat([ser_combo, ser_mono]), labels)
            t_x.at[row, 'p-value'] = '' if pd.isna(p) else f"{p:.3f}"
        else:
            t_x.at[row, 'p-value'] = ''

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
    t_x.at['Combination therapy', 'Subgroup monotherapy (n=33)'] = fmt_pct(0, len(mono))
    t_x.at['Combination therapy', 'Subgroup combination (n=57)'] = fmt_pct(len(combo), len(combo))
    t_x.at['Combination therapy', 'p-value'] = ''
    t_x.at['Monotherapy', 'Primary Cohort (n=104)'] = fmt_pct(int(mon_t.sum()), len(total))
    t_x.at['Monotherapy', 'Subgroup monotherapy (n=33)'] = fmt_pct(len(mono), len(mono))
    t_x.at['Monotherapy', 'Subgroup combination (n=57)'] = fmt_pct(0, len(combo))
    t_x.at['Monotherapy', 'p-value'] = ''
    t_x.loc['Last line therapy\u00b2, n (%)'] = ''
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
    p = p_cont(pd.concat([days_c, days_m]).reset_index(drop=True), labels)
    t_x.at['Median duration, days (IQR)', 'p-value'] = '' if pd.isna(p) else f"{p:.3f}"
    t_x.at['Duration range, days', 'p-value'] = ''
    t_y_rows = [
        'N=',
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
    t_y.at['N=', 'Primary Cohort (n=104)'] = len(total)
    t_y.at['N=', 'Subgroup monotherapy (n=33)'] = len(mono)
    t_y.at['N=', 'Subgroup combination (n=57)'] = len(combo)
    t_y.at['N=', 'p-value'] = ''
    t_y.loc['Underlying conditions, n (%)'] = ''
    t_y.loc['Immunosuppressive treatment, n (%)'] = ''
    t_y.loc['Treatment setting\u00b9, n (%)'] = ''
    age_t = total[COL_AGE]
    age_m = mono[COL_AGE]
    age_c = combo[COL_AGE]
    t_y.at['Age, median (IQR)', 'Primary Cohort (n=104)'] = fmt_iqr(age_t)
    t_y.at['Age, median (IQR)', 'Subgroup monotherapy (n=33)'] = fmt_iqr(age_m)
    t_y.at['Age, median (IQR)', 'Subgroup combination (n=57)'] = fmt_iqr(age_c)
    p = p_cont(pd.concat([age_c, age_m]).reset_index(drop=True), labels)
    t_y.at['Age, median (IQR)', 'p-value'] = '' if pd.isna(p) else f"{p:.3f}"
    female_t = total[COL_SEX].str.lower().str.startswith('f')
    female_m = mono[COL_SEX].str.lower().str.startswith('f')
    female_c = combo[COL_SEX].str.lower().str.startswith('f')

    def add_y(row, ser_total, ser_mono, ser_combo):
        t_y.at[row, 'Primary Cohort (n=104)'] = fmt_pct(int(ser_total.sum()), len(total))
        t_y.at[row, 'Subgroup monotherapy (n=33)'] = fmt_pct(int(ser_mono.sum()), len(mono))
        t_y.at[row, 'Subgroup combination (n=57)'] = fmt_pct(int(ser_combo.sum()), len(combo))
        if ser_total.sum():
            p = p_cat(pd.concat([ser_combo, ser_mono]), labels)
            t_y.at[row, 'p-value'] = '' if pd.isna(p) else f"{p:.3f}"
        else:
            t_y.at[row, 'p-value'] = ''

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
    p = p_cont(pd.concat([doses_c, doses_m]).reset_index(drop=True), labels)
    t_y.at['Vaccination doses, n (range)', 'p-value'] = '' if pd.isna(p) else f"{p:.3f}"
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
    df_compare = pd.concat([df_combo, df_mono], ignore_index=True)
    group_map = {'Total': df_total, 'Combination': df_combo, 'Monotherapy': df_mono}
    df = df_total

    def chi2_perm(series):
        cats = pd.Categorical(series)
        obs_tab = pd.crosstab(cats, df_compare['therapy'])
        obs = chi2_contingency(obs_tab, correction=False)[0]
        codes = cats.codes
        labels = df_compare['therapy'].values.copy()
        rng = np.random.default_rng(0)
        cnt = 0
        for _ in range(10000):
            rng.shuffle(labels)
            perm = np.zeros(obs_tab.shape)
            for i in range(len(cats.categories)):
                mask = codes == i
                perm[i, 0] = np.sum(labels[mask] == 'Combination')
                perm[i, 1] = np.sum(labels[mask] == 'Monotherapy')
            val = chi2_contingency(perm, correction=False)[0]
            if val >= obs:
                cnt += 1
        return cnt / 10000

    def p_categorical(series):
        mask = df_compare['therapy'].isin(['Combination', 'Monotherapy'])
        if series[mask].nunique() < 2 or mask.sum() == 0:
            return np.nan
        table = pd.crosstab(series[mask], df_compare.loc[mask, 'therapy'])
        exp = np.outer(table.sum(axis=1), table.sum(axis=0)) / table.values.sum()
        if series.nunique() == 2:
            if (exp < 5).any():
                return fisher_exact(table)[1]
            return chi2_contingency(table, correction=False)[1]
        if (exp < 5).any():
            return chi2_perm(series)
        return chi2_contingency(table, correction=False)[1]

    def p_continuous(series):
        g1 = series[df_compare['therapy'] == 'Combination'].dropna()
        g2 = series[df_compare['therapy'] == 'Monotherapy'].dropna()
        if g1.empty or g2.empty:
            return np.nan, 'median'
        n1 = len(g1)
        n2 = len(g2)
        normal = (
            n1 >= 30
            and n2 >= 30
            and (n1 < 3 or shapiro(g1).pvalue > 0.05)
            and (n2 < 3 or shapiro(g2).pvalue > 0.05)
        )
        if normal:
            return ttest_ind(g1, g2, equal_var=False).pvalue, 'mean'
        return mannwhitneyu(g1, g2, alternative='two-sided').pvalue, 'median'

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
    cols = groups + ['p-Value', 'q-Value', 'Sig']
    out = pd.DataFrame(index=rows, columns=cols)
    out.loc['N=', 'Total'] = len(df_total)
    out.loc['N=', 'Combination'] = len(df_combo)
    out.loc['N=', 'Monotherapy'] = len(df_mono)

    p_store = {}

    p_store['Age'], mode_age = p_continuous(df_compare[col_age])
    for g in groups:
        d = group_map[g]
        out.at['Age', g] = fmt_num(d[col_age], mode_age)

    female = df[col_sex].map(is_female)
    for g in groups:
        d = group_map[g]
        out.at['Sex (female)', g] = fmt_count(female.loc[d.index].fillna(False))
    p_store['Sex (female)'] = p_categorical(female.loc[df_compare.index])

    for g in groups:
        d = group_map[g]
        for cat in unique_order(df['disease'].unique(), disease_order):
            out.at[f'  *{cat}*', g] = fmt_count(d['disease'] == cat)
    out.at['Disease group', 'Total'] = ''
    out.at['Disease group', 'Combination'] = ''
    out.at['Disease group', 'Monotherapy'] = ''
    p_store['Disease group'] = p_categorical(df_compare['disease'])
    for cat in unique_order(df['disease'].unique(), disease_order):
        p_store[f'  *{cat}*'] = p_categorical(df_compare['disease'] == cat)

    for g in groups:
        d = group_map[g]
        for cat in unique_order(df['immuno_detail'].unique(), immuno_order):
            out.at[f'  *{cat}*', g] = fmt_count(d['immuno_detail'] == cat)
    out.at['Immunosuppressive treatment', 'Total'] = ''
    out.at['Immunosuppressive treatment', 'Combination'] = ''
    out.at['Immunosuppressive treatment', 'Monotherapy'] = ''
    p_store['Immunosuppressive treatment'] = p_categorical(df_compare['immuno3'])
    for cat in unique_order(df['immuno_detail'].unique(), immuno_order):
        p_store[f'  *{cat}*'] = p_categorical(df_compare['immuno_detail'] == cat)

    for g in groups:
        d = group_map[g]
        out.at['Glucocorticoid use', g] = fmt_count(d['gc'] == 'Yes')
    p_store['Glucocorticoid use'] = p_categorical(df_compare['gc'] == 'Yes')

    for g in groups:
        d = group_map[g]
        out.at['SARS-CoV-2 Vaccination', g] = fmt_count(d['vacc'] == 'Yes')
    for g in groups:
        out.at['Number of vaccine doses', g] = ''
    p_store['SARS-CoV-2 Vaccination'] = p_categorical(df_compare['vacc'] == 'Yes')
    p_store['Number of vaccine doses'] = p_categorical(df_compare['dose_group'])
    for g in groups:
        d = group_map[g]
        for cat in unique_order(df['dose_group'].dropna().unique(), dose_order):
            out.at[f'  *{cat}*', g] = fmt_count(d['dose_group'] == cat)
    for cat in unique_order(df['dose_group'].dropna().unique(), dose_order):
        p_store[f'  *{cat}*'] = p_categorical(df_compare['dose_group'] == cat)

    for g in groups:
        d = group_map[g]
        out.at['Thoracic CT changes', g] = fmt_count(d['ct'] == 'Yes')
    p_store['Thoracic CT changes'] = p_categorical(df_compare['ct'] == 'Yes')

    p_store['Duration of SARS-CoV-2 replication (days)'], mode_rep = p_continuous(df_compare['rep'])
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
    p_store['SARS-CoV-2 genotype'] = p_categorical(df_compare['variant'])
    for cat in unique_order(df['variant'].unique(), var_order):
        p_store[f'  *{cat}*'] = p_categorical(df_compare['variant'] == cat)

    for g in groups:
        d = group_map[g]
        out.at['Prolonged viral shedding (≥14 days)', g] = fmt_count(d['prolonged'])
    p_store['Prolonged viral shedding (≥14 days)'] = p_categorical(df_compare['prolonged'])

    for g in groups:
        d = group_map[g]
        out.at['Survival', g] = fmt_count(d['survival'] == 'Yes')
    p_store['Survival'] = p_categorical(df_compare['survival'] == 'Yes')

    for g in groups:
        d = group_map[g]
        for cat in unique_order(df['adverse'].unique(), ae_order):
            name = 'None (AE)' if cat == 'None' else cat
            out.at[f'  *{name}*', g] = fmt_count(d['adverse'] == cat)
    out.at['Adverse events', 'Total'] = ''
    out.at['Adverse events', 'Combination'] = ''
    out.at['Adverse events', 'Monotherapy'] = ''
    p_store['Adverse events'] = p_categorical(df_compare['adverse'])
    for cat in unique_order(df['adverse'].unique(), ae_order):
        name = 'None (AE)' if cat == 'None' else cat
        p_store[f'  *{name}*'] = p_categorical(df_compare['adverse'] == cat)

    pvals = pd.Series(p_store)
    mask = pvals.notna()
    qs = pd.Series(index=pvals.index, dtype=float)
    qs[mask] = multipletests(pvals[mask], method='fdr_bh')[1]

    out['p-Value'] = pvals.apply(
        lambda x: '<0.001' if x < 0.001 else f'{x:.3f}' if pd.notna(x) else ''
    )
    out['q-Value'] = qs.apply(
        lambda x: '' if pd.isna(x) else ('<0.001' if x < 0.001 else f'{x:.3f}')
    )
    out['Sig'] = qs.apply(
        lambda x: '***'
        if pd.notna(x) and x <= 0.001
        else ('**' if pd.notna(x) and x <= 0.01 else ('*' if pd.notna(x) and x <= 0.05 else ''))
    )
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
    print(tab_z.fillna(''))
    print('Anti-CD-20 umfasst Rituximab, Obinutuzumab, Ocrelizumab, Mosunetuzumab.')
