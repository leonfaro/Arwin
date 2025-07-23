import pandas as pd
from data_preprocessing import (
    TOTAL,
    MONO,
    COMBO,
    COL_AGE,
    COL_SEX,
    COL_DIS,
    COL_BASE,
    COL_GC,
    COL_VACC,
    COL_CT,
    group_immuno,
    parse_vacc,
    fmt_pct,
    fmt_iqr,
    fmt_range,
    chi_or_fisher,
    fmt_p,
    cont_test,
)

COL_REP = 'SARS-CoV-2 replication\n[days]'
COL_GENO = 'SARS-CoV-2 genotype'
COL_SURV = 'survival outcome\n[yes / no]'
COL_AE_TYPE = 'type of adverse event'


def heme_subtype(x):
    s = str(x).lower()
    if 'dlbcl' in s:
        return 'DLBCL'
    if 'all' in s:
        return 'ALL'
    if 'cll' in s and ',' not in s:
        return 'CLL'
    if 'aml' in s:
        return 'AML'
    if 'follicular' in s or s.strip() == 'fl' or ' fl' in s:
        return 'FL'
    if 'nhl' in s or 'lymphoma' in s or 'mcl' in s or 'lpl' in s or 'malt' in s:
        return 'NHL'
    if 'mm' in s or 'pcl' in s or 'myeloma' in s:
        return 'MM'
    if ',' in s or '+' in s:
        return 'Mixed'
    if s.strip():
        return 'Other'
    return None


def auto_subtype(x):
    s = str(x).lower()
    if 'mctd' in s:
        return 'MCTD'
    if 'rheumatoid' in s or s.strip() == 'ra':
        return 'RA'
    if 'crest' in s:
        return 'CREST'
    if 'ms' in s and 'mcl' not in s:
        return 'MS'
    if 'systemic sclerosis' in s:
        return 'Systemic sclerosis'
    if 'ulcerosa' in s:
        return 'Colitis ulcerosa'
    if 'glomerulonephritis' in s:
        return 'Glomerulonephritis'
    if 'nmda' in s:
        return 'NMDA-receptor encephalitis'
    return None


def transp_subtype(x):
    s = str(x).lower()
    if 'lung' in s and 'tx' in s:
        return 'Lung-TX'
    if 'kidney' in s and 'tx' in s:
        return 'Kidney-TX'
    return None


def disease_group(x):
    s = str(x).lower()
    if 'm' in s:
        return 'Haematological malignancy'
    if 't' in s:
        return 'Transplantation'
    if 'a' in s:
        return 'Autoimmune disease'
    return None


def immuno_cat(x):
    g = group_immuno(x)
    if g == 'CD20':
        return 'Anti-CD-20'
    if g == 'CAR-T':
        return 'CAR-T'
    if g == 'none':
        return 'None'
    return 'None'


def geno_cat(x):
    s = str(x).lower()
    if (
        s.startswith('ba.5')
        or s.startswith('ba5')
        or s.startswith('bf')
        or s.startswith('bq')
        or s.startswith('be')
        or s.startswith('ch')
        or s.startswith('eg')
        or s.startswith('fr')
        or s.startswith('jg')
        or s.startswith('hh')
    ):
        return 'BA.5-derived Omicron subvariant'
    if 'ba.2' in s or s.startswith(('ba2', 'xd', 'xay')):
        return 'BA.2-derived Omicron subvariant'
    if 'ba.1' in s or s.startswith('ba1'):
        return 'BA.1-derived Omicron subvariant'
    if s:
        return 'Other'
    return None


def ae_cat(x):
    s = str(x).lower()
    if 'thrombocytopenia' in s:
        return 'Thrombocytopenia'
    if not s or s in {'none', 'n', 'nan'}:
        return 'None'
    return 'Other'


def add_flags(df):
    df = df.copy()
    df['age_vec'] = pd.to_numeric(df[COL_AGE], errors='coerce')
    df['flag_female'] = df[COL_SEX].astype(str).str.lower().str.startswith('f')
    dis = df['baseline disease']
    df['heme'] = dis.map(heme_subtype)
    df['auto'] = dis.map(auto_subtype)
    df['trans'] = dis.map(transp_subtype)
    df['group'] = df[COL_DIS].map(disease_group)
    df['immu'] = df[COL_BASE].map(immuno_cat)
    df['flag_gc'] = df[COL_GC].astype(str).str.lower().str.startswith('y')
    vacc = df[COL_VACC].map(parse_vacc)
    df['vacc_yes'] = vacc.map(lambda x: x[0] == 'Yes')
    df['dose_vec'] = vacc.map(lambda x: x[1])
    df['flag_ct'] = df[COL_CT].astype(str).str.lower().str.startswith('y')
    df['rep_vec'] = pd.to_numeric(df[COL_REP], errors='coerce')
    df['geno'] = df[COL_GENO].map(geno_cat)
    df['flag_long'] = df['rep_vec'] >= 14
    df['flag_surv'] = df[COL_SURV].astype(str).str.lower().str.startswith('y')
    df['adv'] = df[COL_AE_TYPE].map(ae_cat)
    return df


TOTAL = add_flags(TOTAL)
MONO = add_flags(MONO)
COMBO = add_flags(COMBO)

index = pd.MultiIndex.from_tuples(
    [
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
    'Primary Cohort (n=104)',
    'Subgroup monotherapy (n=33)',
    'Subgroup combination (n=57)',
    'p-value',
]

table_z = pd.DataFrame(index=index, columns=columns)


def add_rate(row, ft, fm, fc):
    nt = int(ft.sum())
    nm = int(fm.sum())
    nc = int(fc.sum())
    table_z.at[row, 'Primary Cohort (n=104)'] = fmt_pct(nt, len(ft))
    table_z.at[row, 'Subgroup monotherapy (n=33)'] = fmt_pct(nm, len(fm))
    table_z.at[row, 'Subgroup combination (n=57)'] = fmt_pct(nc, len(fc))
    p = chi_or_fisher(nc, len(fc) - nc, nm, len(fm) - nm)
    table_z.at[row, 'p-value'] = fmt_p(p)


def add_median_iqr(row, vt, vm, vc):
    vt = pd.to_numeric(vt, errors='coerce').dropna()
    vm = pd.to_numeric(vm, errors='coerce').dropna()
    vc = pd.to_numeric(vc, errors='coerce').dropna()
    table_z.at[row, 'Primary Cohort (n=104)'] = fmt_iqr(vt)
    table_z.at[row, 'Subgroup monotherapy (n=33)'] = fmt_iqr(vm)
    table_z.at[row, 'Subgroup combination (n=57)'] = fmt_iqr(vc)
    table_z.at[row, 'p-value'] = fmt_p(cont_test(vm, vc))


def add_range(row, vt, vm, vc):
    vt = pd.to_numeric(vt, errors='coerce').dropna()
    vm = pd.to_numeric(vm, errors='coerce').dropna()
    vc = pd.to_numeric(vc, errors='coerce').dropna()
    table_z.at[row, 'Primary Cohort (n=104)'] = fmt_range(vt)
    table_z.at[row, 'Subgroup monotherapy (n=33)'] = fmt_range(vm)
    table_z.at[row, 'Subgroup combination (n=57)'] = fmt_range(vc)
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
            TOTAL['heme'] == lab,
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
            TOTAL['auto'] == lab,
            MONO['auto'] == lab,
            COMBO['auto'] == lab,
        )
    for lab in ['Lung-TX', 'Kidney-TX']:
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
    for lab in ['None', 'Anti-CD-20', 'CAR-T']:
        add_rate(
            ('Immunosuppressive treatment, n (%)', lab),
            TOTAL['immu'] == lab,
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
    return table_z


if __name__ == '__main__':
    print('Table Z')
    print(build_table_z().to_string())
