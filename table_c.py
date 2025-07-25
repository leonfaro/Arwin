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
    return table_c


if __name__ == '__main__':
    print('Table C. Detailed Patient Characteristics.')
    print(build_table_c().to_string())
