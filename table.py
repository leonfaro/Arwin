import pandas as pd
import numpy as np
from scipy.stats import fisher_exact, chi2_contingency, mannwhitneyu, shapiro, ttest_ind
from statsmodels.stats.multitest import multipletests

df = pd.read_excel("Data.xlsx", sheet_name=0)
therapy = (
    df[df.columns[17]].str.strip().str[0].map({"c": "Combination", "m": "Monotherapy"})
)
df["therapy"] = therapy


def group_disease(x):
    if not isinstance(x, str):
        return "Unknown"
    s = x.lower()
    if "m" in s:
        return "Haematological malignancy"
    if "t" in s:
        return "Transplantation"
    if "a" in s:
        return "Autoimmune disease"
    return "Unknown"


df["disease"] = df[df.columns[2]].map(group_disease)


def group_immuno(x):
    if not isinstance(x, str):
        return "Unknown"
    s = x.lower()
    if "car-t" in s:
        return "CAR-T"
    if "ritux" in s or "rtx" in s or "cd-20" in s:
        return "Anti-CD-20"
    if "none" in s:
        return "None"
    return "Other"


df["immuno"] = df["baseline therapy"].map(group_immuno)


def flag_gc(x):
    if not isinstance(x, str):
        return "Unknown"
    s = x.lower().strip()
    if s.startswith("n") or "none" in s:
        return "No"
    if s.startswith("y"):
        return "Yes"
    return "Unknown"


df["gc"] = df["any glucocorticosteroid usage? \n[yes / no]"].map(flag_gc)


def parse_vacc(x):
    if not isinstance(x, str):
        return "Unknown", np.nan
    s = x.lower().strip()
    if s.startswith("n"):
        return "No", 0.0
    m = __import__("re").search(r"(\d+)", s)
    return "Yes", float(m.group(1)) if m else np.nan


vacc = df["vaccination [yes / no] (doses) ?"].map(parse_vacc)
df["vacc"] = vacc.map(lambda x: x[0])
df["doses"] = vacc.map(lambda x: x[1])


def group_ct(x):
    if not isinstance(x, str):
        return "Unknown"
    s = x.lower().strip()
    if s.startswith("y"):
        return "Yes"
    if s.startswith("n"):
        return "No"
    return "Unknown"


df["ct"] = df["CT lung changes [yes / no] ?"].map(group_ct)
df["rep"] = pd.to_numeric(df["SARS-CoV-2 replication [days]"], errors="coerce")


def group_variant(x):
    if not isinstance(x, str):
        return "Unknown"
    s = x.upper().strip()
    if s.startswith(
        ("BA.5", "BF", "BQ", "BE", "EG", "HH", "JG", "XBF", "XCH", "FR", "XBB", "XAY")
    ):
        return "BA.5-derived Omicron subvariant"
    if s.startswith(("BA.2", "CH")):
        return "BA.2-derived Omicron subvariant"
    if s.startswith("BA.1"):
        return "BA.1-derived Omicron subvariant"
    return "Other"


df["variant"] = df["SARS-CoV-2 genotype"].map(group_variant)
df["prolonged"] = df["rep"] >= 14


def flag_survival(x):
    if not isinstance(x, str):
        return "Unknown"
    s = x.lower().strip()
    if s.startswith("y"):
        return "Yes"
    if s.startswith("n"):
        return "No"
    return "Unknown"


df["survival"] = df["survival outcome [yes / no] ?"].map(flag_survival)


def group_adv(a, t):
    if isinstance(a, str) and a.lower().startswith("y"):
        t = str(t).lower()
        if "thrombocytopenia" in t:
            return "Thrombocytopenia"
        return "Other"
    if isinstance(a, str) and a.lower().startswith("n"):
        return "None"
    return "Unknown"


df["adverse"] = df.apply(
    lambda r: group_adv(
        r["any adverse events [yes / no] ?"], r["type of adverse event"]
    ),
    axis=1,
)


def chi2_perm(series):
    cats = pd.Categorical(series)
    obs_tab = pd.crosstab(cats, df["therapy"])
    obs = chi2_contingency(obs_tab, correction=False)[0]
    codes = cats.codes
    labels = df["therapy"].values.copy()
    rng = np.random.default_rng(0)
    cnt = 0
    for _ in range(10000):
        rng.shuffle(labels)
        perm = np.zeros(obs_tab.shape)
        for i in range(len(cats.categories)):
            mask = codes == i
            perm[i, 0] = np.sum(labels[mask] == "Combination")
            perm[i, 1] = np.sum(labels[mask] == "Monotherapy")
        val = chi2_contingency(perm, correction=False)[0]
        if val >= obs:
            cnt += 1
    return cnt / 10000


def p_categorical(series):
    table = pd.crosstab(series, df["therapy"])
    exp = np.outer(table.sum(axis=1), table.sum(axis=0)) / table.values.sum()
    if series.nunique() == 2:
        if (exp < 5).any():
            return fisher_exact(table)[1]
        return chi2_contingency(table, correction=False)[1]
    if (exp < 5).any():
        return chi2_perm(series)
    return chi2_contingency(table, correction=False)[1]


def p_continuous(series):
    g1 = series[df["therapy"] == "Combination"].dropna()
    g2 = series[df["therapy"] == "Monotherapy"].dropna()
    if g1.empty or g2.empty:
        return np.nan, "median"
    n1 = len(g1)
    n2 = len(g2)
    normal = (
        n1 >= 30
        and n2 >= 30
        and shapiro(g1).pvalue > 0.05
        and shapiro(g2).pvalue > 0.05
    )
    if normal:
        return ttest_ind(g1, g2, equal_var=False).pvalue, "mean"
    return mannwhitneyu(g1, g2, alternative="two-sided").pvalue, "median"


def fmt_num(x, typ):
    if typ == "mean":
        return f"{x.mean():.1f} ± {x.std():.1f}"
    return f"{int(x.median())} ({int(x.quantile(0.25))}-{int(x.quantile(0.75))})"


def fmt_count(mask):
    return f"{mask.sum()} ({mask.mean()*100:.1f}%)"


rows = [
    "Age",
    "Sex (female)",
    "Disease group",
    "  *Haematological malignancy*",
    "  *Autoimmune disease*",
    "  *Transplantation*",
    "Immunosuppressive treatment",
    "  *None (IS)*",
    "  *Anti-CD-20*",
    "  *CAR-T*",
    "Glucocorticoid use",
    "SARS-CoV-2 Vaccination",
    "Number of vaccine doses",
    "Thoracic CT changes",
    "Duration of SARS-CoV-2 replication (days)",
    "SARS-CoV-2 genotype",
    "  *BA.5-derived Omicron subvariant*",
    "  *BA.2-derived Omicron subvariant*",
    "  *BA.1-derived Omicron subvariant*",
    "  *Other variant*",
    "Prolonged viral shedding (≥14 days)",
    "Survival",
    "Adverse events",
    "  *None (AE)*",
    "  *Thrombocytopenia*",
    "  *Other AE*",
]


groups = ["Total", "Combination", "Monotherapy"]
cols = groups + ["p-Value", "q-Value", "Sig"]
out = pd.DataFrame(index=rows, columns=cols)


p_store = {}

p_store["Age"], mode_age = p_continuous(df["age"])
for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["Age", g] = fmt_num(d["age"], mode_age)

out.at["Sex (female)", "Combination"] = fmt_count(
    (df["therapy"] == "Combination") & (df["sex [male, female]"] == "f")
)
out.at["Sex (female)", "Monotherapy"] = fmt_count(
    (df["therapy"] == "Monotherapy") & (df["sex [male, female]"] == "f")
)
out.at["Sex (female)", "Total"] = fmt_count(df["sex [male, female]"] == "f")
p_store["Sex (female)"] = p_categorical(df["sex [male, female]"] == "f")

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["  *Haematological malignancy*", g] = fmt_count(
        d["disease"] == "Haematological malignancy"
    )
    out.at["  *Autoimmune disease*", g] = fmt_count(
        d["disease"] == "Autoimmune disease"
    )
    out.at["  *Transplantation*", g] = fmt_count(d["disease"] == "Transplantation")
out.at["Disease group", "Total"] = ""
out.at["Disease group", "Combination"] = ""
out.at["Disease group", "Monotherapy"] = ""
p_store["Disease group"] = p_categorical(df["disease"])
p_store["  *Haematological malignancy*"] = p_categorical(
    df["disease"] == "Haematological malignancy"
)
p_store["  *Autoimmune disease*"] = p_categorical(df["disease"] == "Autoimmune disease")
p_store["  *Transplantation*"] = p_categorical(df["disease"] == "Transplantation")

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["  *None (IS)*", g] = fmt_count(d["immuno"] == "None")
    out.at["  *Anti-CD-20*", g] = fmt_count(d["immuno"] == "Anti-CD-20")
    out.at["  *CAR-T*", g] = fmt_count(d["immuno"] == "CAR-T")
out.at["Immunosuppressive treatment", "Total"] = ""
out.at["Immunosuppressive treatment", "Combination"] = ""
out.at["Immunosuppressive treatment", "Monotherapy"] = ""
p_store["Immunosuppressive treatment"] = p_categorical(df["immuno"])
p_store["  *None (IS)*"] = p_categorical(df["immuno"] == "None")
p_store["  *Anti-CD-20*"] = p_categorical(df["immuno"] == "Anti-CD-20")
p_store["  *CAR-T*"] = p_categorical(df["immuno"] == "CAR-T")

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["Glucocorticoid use", g] = fmt_count(d["gc"] == "Yes")
p_store["Glucocorticoid use"] = p_categorical(df["gc"] == "Yes")

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["SARS-CoV-2 Vaccination", g] = fmt_count(d["vacc"] == "Yes")
out["Number of vaccine doses"] = ""
p_store["SARS-CoV-2 Vaccination"] = p_categorical(df["vacc"] == "Yes")
p_store["Number of vaccine doses"], mode_dose = p_continuous(df["doses"])
for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["Number of vaccine doses", g] = fmt_num(d["doses"].dropna(), mode_dose)

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["Thoracic CT changes", g] = fmt_count(d["ct"] == "Yes")
p_store["Thoracic CT changes"] = p_categorical(df["ct"] == "Yes")

p_store["Duration of SARS-CoV-2 replication (days)"], mode_rep = p_continuous(df["rep"])
for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["Duration of SARS-CoV-2 replication (days)", g] = fmt_num(d["rep"], mode_rep)

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["  *BA.5-derived Omicron subvariant*", g] = fmt_count(
        d["variant"] == "BA.5-derived Omicron subvariant"
    )
    out.at["  *BA.2-derived Omicron subvariant*", g] = fmt_count(
        d["variant"] == "BA.2-derived Omicron subvariant"
    )
    out.at["  *BA.1-derived Omicron subvariant*", g] = fmt_count(
        d["variant"] == "BA.1-derived Omicron subvariant"
    )
    out.at["  *Other variant*", g] = fmt_count(d["variant"] == "Other")
out.at["SARS-CoV-2 genotype", "Total"] = ""
out.at["SARS-CoV-2 genotype", "Combination"] = ""
out.at["SARS-CoV-2 genotype", "Monotherapy"] = ""
p_store["SARS-CoV-2 genotype"] = p_categorical(df["variant"])
p_store["  *BA.5-derived Omicron subvariant*"] = p_categorical(
    df["variant"] == "BA.5-derived Omicron subvariant"
)
p_store["  *BA.2-derived Omicron subvariant*"] = p_categorical(
    df["variant"] == "BA.2-derived Omicron subvariant"
)
p_store["  *BA.1-derived Omicron subvariant*"] = p_categorical(
    df["variant"] == "BA.1-derived Omicron subvariant"
)
p_store["  *Other variant*"] = p_categorical(df["variant"] == "Other")

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["Prolonged viral shedding (≥14 days)", g] = fmt_count(d["prolonged"])
p_store["Prolonged viral shedding (≥14 days)"] = p_categorical(df["prolonged"])

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["Survival", g] = fmt_count(d["survival"] == "Yes")
p_store["Survival"] = p_categorical(df["survival"] == "Yes")

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["  *None (AE)*", g] = fmt_count(d["adverse"] == "None")
    out.at["  *Thrombocytopenia*", g] = fmt_count(d["adverse"] == "Thrombocytopenia")
    out.at["  *Other AE*", g] = fmt_count(d["adverse"] == "Other")
out.at["Adverse events", "Total"] = ""
out.at["Adverse events", "Combination"] = ""
out.at["Adverse events", "Monotherapy"] = ""
p_store["Adverse events"] = p_categorical(df["adverse"])
p_store["  *None (AE)*"] = p_categorical(df["adverse"] == "None")
p_store["  *Thrombocytopenia*"] = p_categorical(df["adverse"] == "Thrombocytopenia")
p_store["  *Other AE*"] = p_categorical(df["adverse"] == "Other")


pvals = pd.Series(p_store)
mask = pvals.notna()
qs = pd.Series(index=pvals.index, dtype=float)
qs[mask] = multipletests(pvals[mask], method="fdr_bh")[1]

out["p-Value"] = pvals.apply(lambda x: "<0.001" if x < 0.001 else f"{x:.3f}")
out["q-Value"] = qs.apply(
    lambda x: "" if pd.isna(x) else ("<0.001" if x < 0.001 else f"{x:.3f}")
)
out["Sig"] = qs.apply(
    lambda x: (
        "***"
        if pd.notna(x) and x <= 0.001
        else (
            "**"
            if pd.notna(x) and x <= 0.01
            else ("*" if pd.notna(x) and x <= 0.05 else "")
        )
    )
)

out1 = out
code_v2 = r"""
import pandas as pd

wb = "Data.xlsx"
d_tot = pd.read_excel(wb, sheet_name="PrimaryCohort,n=104")
d_mon = pd.read_excel(wb, sheet_name="CohortMonoTherapy,n=29")
d_com = pd.read_excel(wb, sheet_name="CohortComboTherapy,n=56")
key = ["first author\n(year)", "study specific case/patient ID number"]
extra = d_tot[key + ["baseline disease", "baseline therapy"]]
d_mon = d_mon.merge(extra, on=key, how="left")
d_com = d_com.merge(extra, on=key, how="left")
for df in (d_tot, d_mon, d_com):
    df.columns = df.columns.str.strip()
for df in (d_mon, d_com):
    b = [c for c in df.columns if c.startswith("baseline disease")]
    df["baseline disease"] = df[b].bfill(axis=1).iloc[:, 0]
    df.drop([c for c in b if c != "baseline disease"], axis=1, inplace=True)

def group_disease(x):
    s = str(x).lower()
    if "t" in s:
        return "Transplantation"
    if "m" in s:
        return "Haematological malignancy"
    return "Autoimmune disease"

def immuno(x):
    if not isinstance(x, str):
        return "None"
    s = x.lower()
    if "car-t" in s:
        return "CAR-T"
    if "ritux" in s or "rtx" in s or "cd-20" in s:
        return "Anti-CD-20"
    if "none" in s:
        return "None"
    return "None"

def gc_flag(x):
    if not isinstance(x, str):
        return "No"
    s = x.lower().strip()
    if s.startswith("n") or "none" in s:
        return "No"
    return "Yes"

def vacc(x):
    if not isinstance(x, str):
        return "No", 0
    s = x.lower().strip()
    if s.startswith("n"):
        return "No", 0
    import re
    m = re.search(r"(\d+)", s)
    return "Yes", int(m.group(1)) if m else 0

def ct_flag(x):
    if not isinstance(x, str):
        return "Unknown"
    s = x.lower().strip()
    if s.startswith("y"):
        return "Yes"
    if s.startswith("n"):
        return "No"
    return "Unknown"

def variant(x):
    if not isinstance(x, str):
        return "Other"
    s = x.upper()
    if s.startswith(
        (
            "BA.5",
            "BF",
            "BQ",
            "BE",
            "EG",
            "HH",
            "JG",
            "XBF",
            "XCH",
            "FR",
            "XBB",
            "XAY",
        )
    ):
        return "BA.5-derived Omicron subvariant"
    if s.startswith(("BA.2", "CH", "XCH")):
        return "BA.2-derived Omicron subvariant"
    if s.startswith("BA.1"):
        return "BA.1-derived Omicron subvariant"
    return "Other"

def disease_sub(x):
    s = str(x).upper()
    if "DLBCL" in s:
        return "DLBCL"
    if "ALL" in s:
        return "ALL"
    if "CLL" in s:
        return "CLL"
    if "AML" in s:
        return "AML"
    if "MDS" in s:
        return "MDS"
    if "NHL" in s:
        return "NHL"
    if "MM" in s:
        return "MM"
    if "," in s or "+" in s:
        return "Mixed"
    return "Other"

def auto_sub(x):
    s = str(x).lower()
    if "rheumatoid" in s:
        return "RA"
    if "myositis" in s:
        return "Myositis"
    if "crest" in s:
        return "CREST"
    if s.startswith("ms"):
        return "MS"
    if "systemic sclerosis" in s:
        return "Systemic sclerosis"
    if "colitis" in s:
        return "Colitis ulcerosa"
    if "glomerulonephritis" in s:
        return "Glomerulonephritis"
    if "nmda" in s:
        return "NMDA-receptor encephalitis"
    return "Other"

def tx_sub(x):
    s = str(x)
    if "Lung-TX" in s:
        return "Lung-TX"
    if "Kidney-TX" in s:
        return "Kidney-TX"
    return "Other"

for df in (d_tot, d_mon, d_com):
    df["disease"] = df[
        "Baseline disease cohort \n[a=autoimmunity, m=malignancy, t=transplant]"
    ].apply(group_disease)
    df["immuno"] = df["baseline therapy"].apply(immuno)
    gc_col = df.columns[df.columns.str.contains("glucocortico", case=False)][0]
    df["gc"] = df[gc_col].apply(gc_flag)
    v = df["vaccination [yes / no] (doses) ?"].map(vacc)
    df["vacc"] = v.map(lambda x: x[0])
    df["doses"] = v.map(lambda x: x[1])
    ct_col = df.columns[df.columns.str.contains("CT lung")][0]
    df["ct"] = df[ct_col].apply(ct_flag)
    df["rep"] = pd.to_numeric(df["SARS-CoV-2 replication [days]"], errors="coerce")
    gen = df.columns[df.columns.str.contains("genotype")]
    df["variant"] = df[gen[0]].apply(variant) if len(gen) else "Other"
    df["prolonged"] = df["rep"] >= 14
    df["disease_sub"] = df["baseline disease"].apply(disease_sub)
    df["auto_sub"] = df["baseline disease"].apply(auto_sub)
    df["tx_sub"] = df["baseline disease"].apply(tx_sub)

groups = {
    "Total": d_tot,
    "Combination": d_com,
    "Monotherapy": d_mon,
}

rows = [
    "Age",
    "Sex (female)",
    "Haematological malignancy",
    "  *Other*",
    "  *DLBCL*",
    "  *ALL*",
    "  *CLL*",
    "  *AML*",
    "  *MDS*",
    "  *NHL*",
    "  *MM*",
    "  *Mixed*",
    "Autoimmune disease",
    "  *RA*",
    "  *Myositis*",
    "  *CREST*",
    "  *MS*",
    "  *Systemic sclerosis*",
    "  *Colitis ulcerosa*",
    "  *Glomerulonephritis*",
    "  *NMDA-receptor encephalitis*",
    "Transplantation",
    "  *Lung-TX*",
    "  *Kidney-TX*",
    "Immunosuppressive treatment",
    "  *None*",
    "  *Anti-CD-20*",
    "  *CAR-T*",
    "Glucocorticoid use",
    "SARS-CoV2 Vaccination",
    "Number of vaccine doses",
    "Thoracic CT changes",
    "Duration of SARS-CoV2 replication (days)",
    "SARS-CoV2 genotype",
    "  *BA.5-derived Omicron subvariant*",
    "  *BA.2-derived Omicron subvariant*",
    "  *BA.1-derived Omicron subvariant*",
    "  *Other*",
    "Prolonged viral shedding (≥ 14 days)",
]

out = pd.DataFrame(index=rows, columns=list(groups))
out.index.name = "N="

def age_fmt(x):
    return f"{int(x.median())} ({int(x.quantile(.25))}-{int(x.quantile(.75))})"

def fill(df, row, mask, col):
    out.at[row, col] = f"{mask.sum()} ({mask.mean()*100:.1f}%)"

for col, df in groups.items():
    out.at["Age", col] = age_fmt(df["age"])
    fill(df, "Sex (female)", df["sex [male, female]"] == "f", col)
    fill(df, "  *Other*", df["disease_sub"] == "Other", col)
    fill(df, "  *DLBCL*", df["disease_sub"] == "DLBCL", col)
    fill(df, "  *ALL*", df["disease_sub"] == "ALL", col)
    fill(df, "  *CLL*", df["disease_sub"] == "CLL", col)
    fill(df, "  *AML*", df["disease_sub"] == "AML", col)
    fill(df, "  *MDS*", df["disease_sub"] == "MDS", col)
    fill(df, "  *NHL*", df["disease_sub"] == "NHL", col)
    fill(df, "  *MM*", df["disease_sub"] == "MM", col)
    fill(df, "  *Mixed*", df["disease_sub"] == "Mixed", col)
    mask = df["disease"] == "Haematological malignancy"
    out.at["Haematological malignancy", col] = f"{mask.sum()} ({mask.mean()*100:.1f}%)"
    fill(df, "  *RA*", df["auto_sub"] == "RA", col)
    fill(df, "  *Myositis*", df["auto_sub"] == "Myositis", col)
    fill(df, "  *CREST*", df["auto_sub"] == "CREST", col)
    fill(df, "  *MS*", df["auto_sub"] == "MS", col)
    fill(df, "  *Systemic sclerosis*", df["auto_sub"] == "Systemic sclerosis", col)
    fill(df, "  *Colitis ulcerosa*", df["auto_sub"] == "Colitis ulcerosa", col)
    fill(df, "  *Glomerulonephritis*", df["auto_sub"] == "Glomerulonephritis", col)
    fill(df, "  *NMDA-receptor encephalitis*", df["auto_sub"] == "NMDA-receptor encephalitis", col)
    mask = df["disease"] == "Autoimmune disease"
    out.at["Autoimmune disease", col] = f"{mask.sum()} ({mask.mean()*100:.1f}%)"
    fill(df, "  *Lung-TX*", df["tx_sub"] == "Lung-TX", col)
    fill(df, "  *Kidney-TX*", df["tx_sub"] == "Kidney-TX", col)
    mask = df["disease"] == "Transplantation"
    out.at["Transplantation", col] = f"{mask.sum()} ({mask.mean()*100:.1f}%)"
    fill(df, "  *None*", df["immuno"] == "None", col)
    fill(df, "  *Anti-CD-20*", df["immuno"] == "Anti-CD-20", col)
    fill(df, "  *CAR-T*", df["immuno"] == "CAR-T", col)
    out.at["Immunosuppressive treatment", col] = f"{len(df)} (100.0%)"
    fill(df, "Glucocorticoid use", df["gc"] == "Yes", col)
    fill(df, "SARS-CoV2 Vaccination", df["vacc"] == "Yes", col)
    out.at["Number of vaccine doses", col] = f"{int(df['doses'].median())}"
    fill(df, "Thoracic CT changes", df["ct"] == "Yes", col)
    out.at["Duration of SARS-CoV2 replication (days)", col] = f"{int(df['rep'].median())}"
    fill(
        df,
        "  *BA.5-derived Omicron subvariant*",
        df["variant"] == "BA.5-derived Omicron subvariant",
        col,
    )
    fill(
        df,
        "  *BA.2-derived Omicron subvariant*",
        df["variant"] == "BA.2-derived Omicron subvariant",
        col,
    )
    fill(
        df,
        "  *BA.1-derived Omicron subvariant*",
        df["variant"] == "BA.1-derived Omicron subvariant",
        col,
    )
    fill(df, "  *Other*", df["variant"] == "Other", col)
    fill(df, "Prolonged viral shedding (≥ 14 days)", df["prolonged"], col)
"""
ns = {}
exec(code_v2, ns)
out2 = ns["out"]
a = out1[~out1.index.duplicated()]
b = out2[~out2.index.duplicated()]
idx = a.index.union(b.index)
col = a.columns.union(b.columns)
res = pd.DataFrame(index=idx, columns=col)
res.update(a)
res.update(b)
res.index.name = "N="
order = ["Total", "Combination", "Monotherapy", "p-Value", "q-Value", "Sig"]
out = res.loc[:, [c for c in order if c in res.columns]]

if __name__ == "__main__":
    print(out.fillna(""))
