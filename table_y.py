import pandas as pd
from data_preprocessing import (
    TOTAL,
    MONO,
    COMBO,
    COL_THERAPY,
    fmt_pct,
    chi_or_fisher,
    fmt_p,
    fmt_iqr,
    fmt_range,
    cont_test,
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

table_y = pd.DataFrame(index=index, columns=columns)
table_y_raw = pd.DataFrame(index=index, columns=columns)
table_y.loc[('N =', '')] = [len(TOTAL), len(MONO), len(COMBO), '']
table_y_raw.loc[('N =', '')] = [len(TOTAL), len(MONO), len(COMBO), None]

TOTAL_104 = TOTAL[TOTAL[COL_THERAPY].astype(str).str.startswith(('m', 'c'))]


def add_rate(row, flag_total, flag_mono, flag_combo):
    nt = int(flag_total.sum())
    nm = int(flag_mono.sum())
    nc = int(flag_combo.sum())
    table_y.at[row, 'Total'] = fmt_pct(nt, len(flag_total))
    table_y.at[row, 'Monotherapy'] = fmt_pct(nm, len(flag_mono))
    table_y.at[row, 'Combination'] = fmt_pct(nc, len(flag_combo))
    a11 = nc
    a12 = len(flag_combo) - nc
    a21 = nm
    a22 = len(flag_mono) - nm
    p = chi_or_fisher(a11, a12, a21, a22)
    table_y.at[row, 'p-value'] = fmt_p(p)
    table_y_raw.at[row, 'Total'] = nt
    table_y_raw.at[row, 'Monotherapy'] = nm
    table_y_raw.at[row, 'Combination'] = nc
    table_y_raw.at[row, 'p-value'] = p


def add_median_iqr(row, vec_total, vec_mono, vec_combo):
    vt = pd.to_numeric(vec_total, errors='coerce').dropna()
    vm = pd.to_numeric(vec_mono, errors='coerce').dropna()
    vc = pd.to_numeric(vec_combo, errors='coerce').dropna()
    table_y.at[row, 'Total'] = fmt_iqr(vt)
    table_y.at[row, 'Monotherapy'] = fmt_iqr(vm)
    table_y.at[row, 'Combination'] = fmt_iqr(vc)
    p = cont_test(vm, vc)
    table_y.at[row, 'p-value'] = fmt_p(p)
    table_y_raw.at[row, 'Total'] = vt.median()
    table_y_raw.at[row, 'Monotherapy'] = vm.median()
    table_y_raw.at[row, 'Combination'] = vc.median()
    table_y_raw.at[row, 'p-value'] = p


def add_mean_range(row, vec_total, vec_mono, vec_combo):
    vt = pd.to_numeric(vec_total, errors='coerce').dropna()
    vm = pd.to_numeric(vec_mono, errors='coerce').dropna()
    vc = pd.to_numeric(vec_combo, errors='coerce').dropna()
    table_y.at[row, 'Total'] = f"{vt.mean():.1f} ({fmt_range(vt)})"
    table_y.at[row, 'Monotherapy'] = f"{vm.mean():.1f} ({fmt_range(vm)})"
    table_y.at[row, 'Combination'] = f"{vc.mean():.1f} ({fmt_range(vc)})"
    p = cont_test(vm, vc)
    table_y.at[row, 'p-value'] = fmt_p(p)
    table_y_raw.at[row, 'Total'] = vt.mean()
    table_y_raw.at[row, 'Monotherapy'] = vm.mean()
    table_y_raw.at[row, 'Combination'] = vc.mean()
    table_y_raw.at[row, 'p-value'] = p


def build_table_y():
    table_y.loc[:] = None
    table_y_raw.loc[:] = None
    table_y.loc[('N =', '')] = [len(TOTAL), len(MONO), len(COMBO), '']
    table_y_raw.loc[('N =', '')] = [len(TOTAL), len(MONO), len(COMBO), None]
    add_median_iqr(('Age, median (IQR)', ''), TOTAL_104['age_vec'], MONO['age_vec'], COMBO['age_vec'])
    add_rate(('Female sex, n (%)', ''), TOTAL_104['flag_female'], MONO['flag_female'], COMBO['flag_female'])
    table_y.loc[('Underlying conditions, n (%)', '')] = ''
    table_y_raw.loc[('Underlying conditions, n (%)', '')] = None
    pairs = [
        ('Hematological malignancy', 'flag_malign'),
        ('Autoimmune', 'flag_autoimm'),
        ('Transplantation', 'flag_transpl'),
    ]
    for lbl, col in pairs:
        add_rate(('Underlying conditions, n (%)', lbl), TOTAL_104[col], MONO[col], COMBO[col])
    table_y.loc[('Immunosuppressive treatment, n (%)', '')] = ''
    table_y_raw.loc[('Immunosuppressive treatment, n (%)', '')] = None
    pairs = [
        ('Anti-CD20', 'flag_cd20'),
        ('CAR-T', 'flag_cart'),
        ('HSCT', 'flag_hsct'),
        ('None', 'flag_immuno_none'),
    ]
    for lbl, col in pairs:
        add_rate(('Immunosuppressive treatment, n (%)', lbl), TOTAL_104[col], MONO[col], COMBO[col])
    add_rate(('Glucocorticoid use, n (%)', ''), TOTAL_104['flag_gc'], MONO['flag_gc'], COMBO['flag_gc'])
    add_rate(('SARS-CoV-2 vaccination, n (%)', ''), TOTAL_104['vacc_yes'], MONO['vacc_yes'], COMBO['vacc_yes'])
    add_mean_range(
        ('Mean Vaccination doses, n (range)', ''),
        TOTAL_104['dose_vec'],
        MONO['dose_vec'],
        COMBO['dose_vec'],
    )
    add_rate(('Thoracic CT changes, n (%)', ''), TOTAL_104['flag_ct'], MONO['flag_ct'], COMBO['flag_ct'])

    table_y.loc[('Treatment setting\u00b9, n (%)', '')] = ''
    table_y_raw.loc[('Treatment setting\u00b9, n (%)', '')] = None
    add_rate(
        ('Treatment setting\u00b9, n (%)', 'Hospital'),
        TOTAL_104['flag_hosp'],
        MONO['flag_hosp'],
        COMBO['flag_hosp'],
    )
    add_rate(
        ('Treatment setting\u00b9, n (%)', 'Outpatient'),
        ~TOTAL_104['flag_hosp'],
        ~MONO['flag_hosp'],
        ~COMBO['flag_hosp'],
    )
    foot = (
        '- NMV-r, nirmatrelvir-ritonavir.\n'
        '1: Treatment setting where prolonged NMV-r was administered.'
    )
    table_y.attrs['footnote'] = foot
    table_y_raw.attrs['footnote'] = foot
    return table_y


def build_table_y_raw():
    if table_y_raw.isnull().all().all():
        build_table_y()
    return table_y_raw


if __name__ == '__main__':
    tab = build_table_y()
    tab.to_excel('table_y_v7.xlsx')
    build_table_y_raw().to_csv('table_y_v7.csv')
    print(tab.shape)
    print('Table Y. Demographics and Clinical Characteristics.')
    print(build_table_y().to_string())
    print('- NMV-r, nirmatrelvir-ritonavir.')
    print('1: Treatment setting where prolonged NMV-r was administered.')

__all__ = [
    'table_y',
    'table_y_raw',
    'TOTAL',
    'MONO',
    'COMBO',
    'build_table_y',
    'build_table_y_raw',
    'add_rate',
    'add_median_iqr',
    'add_mean_range',
]
