import pandas as pd
from data_preprocessing import (
    TOTAL,
    MONO,
    COMBO,
    COL_BASE,
    fill_rate,
    fill_median_iqr,
    fill_mean_range,
    fmt_p,
)

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
