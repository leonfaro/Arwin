import pandas as pd

wb='Data.xlsx'
df=pd.read_excel(wb, sheet_name=0)
therapy=df[df.columns[17]].str.strip().str[0].map({'c':'Combination','m':'Monotherapy'})
df['therapy']=therapy


def group_disease(x):
    s=str(x)
    if 'm' in s:
        return 'Haematological malignancy'
    if 't' in s:
        return 'Transplantation'
    if 'a' in s:
        return 'Autoimmune disease'
    return 'Autoimmune disease'

df['disease']=df[df.columns[2]].apply(group_disease)


def group_immuno(x):
    if not isinstance(x,str):
        return 'None'
    s=x.lower()
    if 'car-t' in s:
        return 'CAR-T'
    if 'ritux' in s or 'rtx' in s or 'cd-20' in s:
        return 'Anti-CD-20'
    if 'none' in s:
        return 'None'
    return 'None'

df['immuno']=df['baseline therapy'].apply(group_immuno)


def flag_gc(x):
    if not isinstance(x,str):
        return 'No'
    s=x.lower().strip()
    if s.startswith('n') or 'none' in s:
        return 'No'
    return 'Yes'

df['gc']=df['any glucocorticosteroid usage? \n[yes / no]'].apply(flag_gc)


def parse_vacc(x):
    if not isinstance(x,str):
        return 'No',0
    s=x.lower().strip()
    if s.startswith('n'):
        return 'No',0
    import re
    m=re.search(r'(\d+)',s)
    return 'Yes',int(m.group(1)) if m else 0

vacc=df['vaccination [yes / no] (doses) ?'].map(parse_vacc)
df['vacc']=vacc.map(lambda x:x[0])
df['doses']=vacc.map(lambda x:x[1])


def group_ct(x):
    if not isinstance(x,str):
        return 'Unknown'
    s=x.lower().strip()
    if s.startswith('y'):
        return 'Yes'
    if s.startswith('n'):
        return 'No'
    return 'Unknown'

df['ct']=df['CT lung changes [yes / no] ?'].apply(group_ct)

df['rep']=pd.to_numeric(df['SARS-CoV-2 replication [days]'],errors='coerce')


def group_variant(x):
    if not isinstance(x,str):
        return 'Other'
    s=x.upper()
    if s.startswith(('BA.5','BF','BQ','BE','EG','HH','JG','XBF','XCH','FR','XBB','XAY')):
        return 'BA.5-derived Omicron subvariant'
    if s.startswith(('BA.2','CH','XCH')):
        return 'BA.2-derived Omicron subvariant'
    if s.startswith('BA.1'):
        return 'BA.1-derived Omicron subvariant'
    return 'Other'

df['variant']=df['SARS-CoV-2 genotype'].apply(group_variant)
df['prolonged']=df['rep']>=14


def flag_survival(x):
    if not isinstance(x,str):
        return 'No'
    return 'Yes' if x.lower().startswith('y') else 'No'

df['survival']=df['survival outcome [yes / no] ?'].apply(flag_survival)


def group_adv(row):
    a=row['any adverse events [yes / no] ?']
    t=str(row['type of adverse event']).lower()
    if isinstance(a,str) and a.lower().startswith('y'):
        if 'thrombocytopenia' in t:
            return 'Thrombocytopenia'
        return 'Other'
    return 'None'

df['adverse']=df.apply(group_adv,axis=1)

cols=['Total','Combination','Monotherapy']
rows=[
    'Age',
    'Sex (female)',
    'Disease group',
    '  *Haematological malignancy*',
    '  *Autoimmune disease*',
    '  *Transplantation*',
    'Immunosuppressive treatment',
    '  *None (IS)*',
    '  *Anti-CD-20*',
    '  *CAR-T*',
    'Glucocorticoid use',
    'SARS-CoV-2 Vaccination',
    'Number of vaccine doses',
    'Thoracic CT changes',
    'Duration of SARS-CoV-2 replication (days)',
    'SARS-CoV-2 genotype',
    '  *BA.5-derived Omicron subvariant*',
    '  *BA.2-derived Omicron subvariant*',
    '  *BA.1-derived Omicron subvariant*',
    '  *Other variant*',
    'Prolonged viral shedding (≥14 days)',
    'Survival',
    'Adverse events',
    '  *None (AE)*',
    '  *Thrombocytopenia*',
    '  *Other AE*'
]

out=pd.DataFrame(index=rows,columns=cols)


def age_fmt(x):
    return f"{int(x.median())} ({int(x.quantile(.25))}-{int(x.quantile(.75))})"

def fill(c,row,series):
    out.at[row,c]=f"{series.sum()} ({series.mean()*100:.1f}%)"

for c in cols:
    d=df if c=='Total' else df[df['therapy']==c]
    out.at['Age',c]=age_fmt(d['age'])
    fill(c,'Sex (female)',d['sex [male, female]']=='f')
    fill(c,'  *Haematological malignancy*',d['disease']=='Haematological malignancy')
    fill(c,'  *Autoimmune disease*',d['disease']=='Autoimmune disease')
    fill(c,'  *Transplantation*',d['disease']=='Transplantation')
    fill(c,'  *None (IS)*',d['immuno']=='None')
    fill(c,'  *Anti-CD-20*',d['immuno']=='Anti-CD-20')
    fill(c,'  *CAR-T*',d['immuno']=='CAR-T')
    fill(c,'Glucocorticoid use',d['gc']=='Yes')
    fill(c,'SARS-CoV-2 Vaccination',d['vacc']=='Yes')
    out.at['Number of vaccine doses',c]=f"{int(d['doses'].median())}"
    fill(c,'Thoracic CT changes',d['ct']=='Yes')
    out.at['Duration of SARS-CoV-2 replication (days)',c]=f"{int(d['rep'].median())}"
    fill(c,'  *BA.5-derived Omicron subvariant*',d['variant']=='BA.5-derived Omicron subvariant')
    fill(c,'  *BA.2-derived Omicron subvariant*',d['variant']=='BA.2-derived Omicron subvariant')
    fill(c,'  *BA.1-derived Omicron subvariant*',d['variant']=='BA.1-derived Omicron subvariant')
    fill(c,'  *Other variant*',d['variant']=='Other')
    fill(c,'Prolonged viral shedding (≥14 days)',d['prolonged'])
    fill(c,'Survival',d['survival']=='Yes')
    fill(c,'  *None (AE)*',d['adverse']=='None')
    fill(c,'  *Thrombocytopenia*',d['adverse']=='Thrombocytopenia')
    fill(c,'  *Other AE*',d['adverse']=='Other')

print(out)
