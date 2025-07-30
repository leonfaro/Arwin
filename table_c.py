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
