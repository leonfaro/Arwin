import pandas as pd
from data_preprocessing import (
    TOTAL,
    MONO,
    COMBO,
    COL_THERAPY,
    fmt_pct,
    fmt_iqr,
    fmt_range,
    chi_or_fisher,
    fmt_p,
    cont_test,
)

index = pd.MultiIndex.from_tuples(
    [
        ('N =', ''),
        ('Age, median (IQR)', ''),
        ('Sex (female), n (%)', ''),
        ('Haematological malignancy, n (%)', ''),
        ('Haematological malignancy, n (%)', 'Other'),
        ('Haematological malignancy, n (%)', 'DLBCL'),
        ('Haematological malignancy, n (%)', 'ALL'),
        ('Haematological malignancy, n (%)', 'CLL'),
        ('Haematological malignancy, n (%)', 'AML'),
        ('Haematological malignancy, n (%)', 'FL'),
        ('Haematological malignancy, n (%)', 'NHL'),
        ('Haematological malignancy, n (%)', 'MM'),
        ('Haematological malignancy, n (%)', 'Mixed'),
        ('Autoimmune disease, n (%)', ''),
        ('Autoimmune disease, n (%)', 'MCTD'),
        ('Autoimmune disease, n (%)', 'RA'),
        ('Autoimmune disease, n (%)', 'CREST'),
        ('Autoimmune disease, n (%)', 'MS'),
        ('Autoimmune disease, n (%)', 'Systemic sclerosis'),
        ('Autoimmune disease, n (%)', 'Colitis ulcerosa'),
        ('Autoimmune disease, n (%)', 'Glomerulonephritis'),
        ('Autoimmune disease, n (%)', 'NMDA-receptor encephalitis'),
        ('Transplantation, n (%)', ''),
        ('Transplantation, n (%)', 'Lung-TX'),
        ('Transplantation, n (%)', 'Kidney-TX'),
        ('Disease group, n (%)', ''),
        ('Disease group, n (%)', 'Haematological malignancy'),
        ('Disease group, n (%)', 'Autoimmune disease'),
        ('Disease group, n (%)', 'Transplantation'),
        ('Immunosuppressive treatment, n (%)', ''),
        ('Immunosuppressive treatment, n (%)', 'None'),
        ('Immunosuppressive treatment, n (%)', 'Anti-CD-20'),
        ('Immunosuppressive treatment, n (%)', 'CAR-T'),
        ('Glucocorticoid use, n (%)', ''),
        ('SARS-CoV-2 vaccination, n (%)', ''),
        ('Number of vaccine doses, n (range)', ''),
        ('Thoracic CT changes, n (%)', ''),
        ('Duration of SARS-CoV-2 replication (days), median (IQR)', ''),
        ('SARS-CoV-2 genotype, n (%)', ''),
        ('SARS-CoV-2 genotype, n (%)', 'BA.5-derived Omicron subvariant'),
        ('SARS-CoV-2 genotype, n (%)', 'BA.2-derived Omicron subvariant'),
        ('SARS-CoV-2 genotype, n (%)', 'BA.1-derived Omicron subvariant'),
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

table_z = pd.DataFrame(index=index, columns=columns)
table_z.loc[('N =', '')] = [len(TOTAL), len(MONO), len(COMBO), '']

TOTAL_104 = TOTAL[TOTAL[COL_THERAPY].astype(str).str.startswith(('m', 'c'))]


def add_rate(row, ft, fm, fc):
    nt = int(ft.sum())
    nm = int(fm.sum())
    nc = int(fc.sum())
    table_z.at[row, 'Total'] = fmt_pct(nt, len(ft))
    table_z.at[row, 'Monotherapy'] = fmt_pct(nm, len(fm))
    table_z.at[row, 'Combination'] = fmt_pct(nc, len(fc))
    p = chi_or_fisher(nc, len(fc) - nc, nm, len(fm) - nm)
    table_z.at[row, 'p-value'] = fmt_p(p)


def add_median_iqr(row, vt, vm, vc):
    vt = pd.to_numeric(vt, errors='coerce').dropna()
    vm = pd.to_numeric(vm, errors='coerce').dropna()
    vc = pd.to_numeric(vc, errors='coerce').dropna()
    table_z.at[row, 'Total'] = fmt_iqr(vt)
    table_z.at[row, 'Monotherapy'] = fmt_iqr(vm)
    table_z.at[row, 'Combination'] = fmt_iqr(vc)
    table_z.at[row, 'p-value'] = fmt_p(cont_test(vm, vc))


def add_range(row, vt, vm, vc):
    vt = pd.to_numeric(vt, errors='coerce').dropna()
    vm = pd.to_numeric(vm, errors='coerce').dropna()
    vc = pd.to_numeric(vc, errors='coerce').dropna()
    table_z.at[row, 'Total'] = fmt_range(vt)
    table_z.at[row, 'Monotherapy'] = fmt_range(vm)
    table_z.at[row, 'Combination'] = fmt_range(vc)
    table_z.at[row, 'p-value'] = fmt_p(cont_test(vm, vc))


def build_table_z():
    table_z.loc[:] = None
    table_z.loc[('Haematological malignancy, n (%)', '')] = ''
    table_z.loc[('Autoimmune disease, n (%)', '')] = ''
    table_z.loc[('Transplantation, n (%)', '')] = ''
    table_z.loc[('Disease group, n (%)', '')] = ''
    table_z.loc[('Immunosuppressive treatment, n (%)', '')] = ''
    table_z.loc[('SARS-CoV-2 genotype, n (%)', '')] = ''
    table_z.loc[('Adverse events, n (%)', '')] = ''
    add_median_iqr(('Age, median (IQR)', ''), TOTAL['age_vec'], MONO['age_vec'], COMBO['age_vec'])
    add_rate(('Sex (female), n (%)', ''), TOTAL['flag_female'], MONO['flag_female'], COMBO['flag_female'])
    labs = ['Other', 'DLBCL', 'ALL', 'CLL', 'AML', 'FL', 'NHL', 'MM', 'Mixed']
    for lab in labs:
        add_rate(
            ('Haematological malignancy, n (%)', lab),
            TOTAL_104['heme'] == lab,
            MONO['heme'] == lab,
            COMBO['heme'] == lab,
        )
    labs = [
        'MCTD',
        'RA',
        'CREST',
        'MS',
        'Systemic sclerosis',
        'Colitis ulcerosa',
        'Glomerulonephritis',
        'NMDA-receptor encephalitis',
    ]
    for lab in labs:
        add_rate(
            ('Autoimmune disease, n (%)', lab),
            TOTAL_104['auto'] == lab,
            MONO['auto'] == lab,
            COMBO['auto'] == lab,
        )
    for lab in ['Lung-TX', 'Kidney-TX']:
        add_rate(
            ('Transplantation, n (%)', lab),
            TOTAL_104['trans'] == lab,
            MONO['trans'] == lab,
            COMBO['trans'] == lab,
        )
    for lab in ['Haematological malignancy', 'Autoimmune disease', 'Transplantation']:
        add_rate(
            ('Disease group, n (%)', lab),
            TOTAL_104['group'] == lab,
            MONO['group'] == lab,
            COMBO['group'] == lab,
        )
    for lab in ['None', 'Anti-CD-20', 'CAR-T']:
        add_rate(
            ('Immunosuppressive treatment, n (%)', lab),
            TOTAL_104['immu'] == lab,
            MONO['immu'] == lab,
            COMBO['immu'] == lab,
        )
    add_rate(('Glucocorticoid use, n (%)', ''), TOTAL['flag_gc'], MONO['flag_gc'], COMBO['flag_gc'])
    add_rate(('SARS-CoV-2 vaccination, n (%)', ''), TOTAL['vacc_yes'], MONO['vacc_yes'], COMBO['vacc_yes'])
    add_range(('Number of vaccine doses, n (range)', ''), TOTAL['dose_vec'], MONO['dose_vec'], COMBO['dose_vec'])
    add_rate(('Thoracic CT changes, n (%)', ''), TOTAL['flag_ct'], MONO['flag_ct'], COMBO['flag_ct'])
    add_median_iqr(
        ('Duration of SARS-CoV-2 replication (days), median (IQR)', ''),
        TOTAL['rep_vec'],
        MONO['rep_vec'],
        COMBO['rep_vec'],
    )
    labs = [
        'BA.5-derived Omicron subvariant',
        'BA.2-derived Omicron subvariant',
        'BA.1-derived Omicron subvariant',
        'Other',
    ]
    for lab in labs:
        add_rate(
            ('SARS-CoV-2 genotype, n (%)', lab),
            TOTAL_104['geno'] == lab,
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
        add_rate(('Adverse events, n (%)', lab), TOTAL_104['adv'] == lab, MONO['adv'] == lab, COMBO['adv'] == lab)
    return table_z


if __name__ == '__main__':
    print('Table Z')
    print(build_table_z().to_string())
