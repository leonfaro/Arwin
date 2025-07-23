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
    COL_HOSP,
    group_immuno,
    parse_vacc,
)


def _add_flags(df: pd.DataFrame) -> pd.DataFrame:
    df['flag_female'] = df[COL_SEX].astype(str).str.lower().str.startswith('f')
    s = df[COL_DIS].astype(str).str.lower()
    df['flag_malign'] = s.str.contains('m')
    df['flag_autoimm'] = s.str.contains('a')
    df['flag_transpl'] = s.str.contains('t')
    base = df[COL_BASE].map(group_immuno)
    df['flag_cd20'] = base == 'CD20'
    df['flag_cart'] = base == 'CAR-T'
    df['flag_hsct'] = base == 'HSCT'
    df['flag_immuno_none'] = ~(df[['flag_cd20', 'flag_cart', 'flag_hsct']].any(axis=1)) | (base == 'none')
    df['flag_gc'] = df[COL_GC].astype(str).str.lower().str.startswith('y')
    vacc = df[COL_VACC].map(parse_vacc)
    df['vacc_yes'] = vacc.map(lambda x: x[0] == 'Yes')
    df['vacc_dose'] = vacc.map(lambda x: x[1])
    df['flag_ct'] = df[COL_CT].astype(str).str.lower().str.startswith('y')
    df['flag_hosp'] = df[COL_HOSP].astype(str).str.lower().str.startswith('y')
    df['age_vec'] = pd.to_numeric(df[COL_AGE], errors='coerce')
    df['dose_vec'] = pd.to_numeric(df['vacc_dose'], errors='coerce')
    return df


TOTAL = _add_flags(TOTAL)
MONO = _add_flags(MONO)
COMBO = _add_flags(COMBO)

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

columns = [
    'Primary Cohort (n=104)',
    'Subgroup monotherapy (n=33)',
    'Subgroup combination (n=57)',
    'p-value',
]

table_y = pd.DataFrame(index=index, columns=columns)

table_y_raw = pd.DataFrame(index=index, columns=columns)

__all__ = ['table_y', 'table_y_raw', 'TOTAL', 'MONO', 'COMBO']
