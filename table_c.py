import pandas as pd
from data_preprocessing import (
    TOTAL,
    MONO,
    COMBO,
    fill_rate,
    fill_median_iqr,
    fill_range,
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
        ('Autoimmune disease, n (%)', 'SSc'),
        ('Autoimmune disease, n (%)', 'Colitis ulcerosa'),
        ('Autoimmune disease, n (%)', 'Glomerulonephritis'),
        ('Autoimmune disease, n (%)', 'NMDA-encephalitis'),
        ('Transplantation, n (%)', ''),
        ('Transplantation, n (%)', 'LT'),
        ('Transplantation, n (%)', 'KT'),
        ('Disease group, n (%)', ''),
        ('Disease group, n (%)', 'Haematological malignancy'),
        ('Disease group, n (%)', 'Autoimmune disease'),
        ('Disease group, n (%)', 'Transplantation'),
        ('Immunosuppressive treatment, n (%)', ''),
        ('Immunosuppressive treatment, n (%)', 'None'),
        ('Immunosuppressive treatment, n (%)', 'Anti-CD-20'),
        ('Immunosuppressive treatment, n (%)', 'CAR-T'),
        ('Immunosuppressive treatment, n (%)', 'HSCT'),
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

table_c = pd.DataFrame(index=index, columns=columns)
table_c.loc[('N =', '')] = [len(TOTAL), len(MONO), len(COMBO), '']


def add_rate(row, ft, fm, fc):
    fill_rate(table_c, row, ft, fm, fc)


def add_median_iqr(row, vt, vm, vc):
    fill_median_iqr(table_c, row, vt, vm, vc)


def add_range(row, vt, vm, vc):
    fill_range(table_c, row, vt, vm, vc)


def build_table_c():
    table_c.loc[:] = None
    table_c.loc[('N =', '')] = [len(TOTAL), len(MONO), len(COMBO), '']
    table_c.loc[('Haematological malignancy, n (%)', '')] = ''
    table_c.loc[('Autoimmune disease, n (%)', '')] = ''
    table_c.loc[('Transplantation, n (%)', '')] = ''
    table_c.loc[('Disease group, n (%)', '')] = ''
    table_c.loc[('Immunosuppressive treatment, n (%)', '')] = ''
    table_c.loc[('SARS-CoV-2 genotype, n (%)', '')] = ''
    table_c.loc[('Adverse events, n (%)', '')] = ''
    add_median_iqr(('Age, median (IQR)', ''), TOTAL['age_vec'], MONO['age_vec'], COMBO['age_vec'])
    add_rate(('Sex (female), n (%)', ''), TOTAL['flag_female'], MONO['flag_female'], COMBO['flag_female'])
    labs = ['Other', 'DLBCL', 'ALL', 'CLL', 'AML', 'FL', 'NHL', 'MM', 'Mixed']
    for lab in labs:
        add_rate(
            ('Haematological malignancy, n (%)', lab),
            TOTAL['heme'] == lab,
            MONO['heme'] == lab,
            COMBO['heme'] == lab,
        )
    labs = [
        'MCTD',
        'RA',
        'CREST',
        'MS',
        'SSc',
        'Colitis ulcerosa',
        'Glomerulonephritis',
        'NMDA-encephalitis',
    ]
    for lab in labs:
        add_rate(
            ('Autoimmune disease, n (%)', lab),
            TOTAL['auto'] == lab,
            MONO['auto'] == lab,
            COMBO['auto'] == lab,
        )
    for lab in ['LT', 'KT']:
        add_rate(
            ('Transplantation, n (%)', lab),
            TOTAL['trans'] == lab,
            MONO['trans'] == lab,
            COMBO['trans'] == lab,
        )
    for lab in ['Haematological malignancy', 'Autoimmune disease', 'Transplantation']:
        add_rate(
            ('Disease group, n (%)', lab),
            TOTAL['group'] == lab,
            MONO['group'] == lab,
            COMBO['group'] == lab,
        )
    pairs = [
        ('None', TOTAL['flag_immuno_none'], MONO['flag_immuno_none'], COMBO['flag_immuno_none']),
        ('Anti-CD-20', TOTAL['flag_cd20'], MONO['flag_cd20'], COMBO['flag_cd20']),
        ('CAR-T', TOTAL['flag_cart'], MONO['flag_cart'], COMBO['flag_cart']),
        ('HSCT', TOTAL['flag_hsct'], MONO['flag_hsct'], COMBO['flag_hsct']),
    ]
    for lbl, ft, fm, fc in pairs:
        add_rate(('Immunosuppressive treatment, n (%)', lbl), ft, fm, fc)
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
    return table_c


if __name__ == '__main__':
    print('Table C. Detailed Patient Characteristics.')
    print(build_table_c().to_string())
