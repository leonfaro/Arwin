import pandas as pd
from data_preprocessing import (
    TOTAL,
    MONO,
    COMBO,
    DF_mono,
    DF_comb,
    COL_AGE,
    COL_SEX,
    COL_DIS,
    COL_BASE,
    COL_GC,
    COL_VACC,
    COL_CT,
    COL_HOSP,
    group_immuno,
    parse_vacc,
    cont_test,
    chi_or_fisher,
    fmt_p,
)


def build_table_y():
    index = pd.MultiIndex.from_tuples(
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
    t_y = pd.DataFrame(index=index, columns=[
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
    for label, frame in {'Primary Cohort': TOTAL, 'Subgroup monotherapy': MONO, 'Subgroup combination': COMBO}.items():
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
    return t_y
