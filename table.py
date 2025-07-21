import pandas as pd
import numpy as np
from scipy.stats import fisher_exact, chi2_contingency, mannwhitneyu, shapiro, ttest_ind
from statsmodels.stats.multitest import multipletests

df = pd.read_excel("Data.xlsx", sheet_name=0)
col = "any previous NMV-r treatment …"
therapy = df[col].str.strip().str[0].map({"c": "Combination", "m": "Monotherapy"})
df["therapy"] = therapy


def group_disease(x):
    if not isinstance(x, str):
        return "Unknown"
    s = x.lower()
    a = "a" in s
    m = "m" in s
    t = "t" in s
    n = a + m + t
    if n > 1:
        return "Mixed"
    if a:
        return "Autoimmune disease"
    if m:
        return "Haematological malignancy"
    if t:
        return "Transplantation"
    return "Unknown"


df["disease"] = df[df.columns[2]].map(group_disease)
mixed_count = (df["disease"] == "Mixed").sum()
use_mixed = mixed_count >= 5
if not use_mixed:
    df.loc[df["disease"] == "Mixed", "disease"] = "Transplantation"


def group_immuno_detail(x):
    if not isinstance(x, str) or not x.strip():
        return "None"
    s = x.lower()
    k = (
        "ritux",
        "rtx",
        "obinutuzumab",
        "obinu",
        "obi",
        "ocrelizumab",
        "ocre",
        "ocr",
        "mosunetuzumab",
        "mosu",
        "mos",
    )
    if any(i in s for i in k):
        return "Anti-CD-20"
    if "none" in s or "no is" in s:
        return "None"
    return "Other"


df["immuno_detail"] = df["baseline therapy"].map(group_immuno_detail)
df["immuno3"] = df["immuno_detail"].map(
    lambda x: "Anti-CD-20" if x == "Anti-CD-20" else ("None" if x == "None" else "Other")
)


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


def group_dose(x):
    if pd.isna(x):
        return np.nan
    if x >= 5:
        return "≥5"
    if x >= 3:
        return "3-4"
    if x >= 1:
        return "1-2"
    return "0"


df["dose_group"] = df["doses"].map(group_dose)


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
    if s.startswith("BQ.1"):
        return "BQ.1.x"
    if s.startswith("BA.5"):
        return "BA.5.x"
    if s.startswith("BA.2"):
        return "BA.2.x"
    if s.startswith("BA.1"):
        return "BA.1.x"
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
]
if use_mixed:
    rows.append("  *Mixed*")
rows += [
    "Immunosuppressive treatment",
    "  *Anti-CD-20*",
    "  *Other*",
    "  *None*",
    "Glucocorticoid use",
    "SARS-CoV-2 Vaccination",
    "Number of vaccine doses",
    "  *0*",
    "  *1-2*",
    "  *3-4*",
    "  *≥5*",
    "Thoracic CT changes",
    "Duration of SARS-CoV-2 replication (days)",
    "SARS-CoV-2 genotype",
    "  *BA.1.x*",
    "  *BA.2.x*",
    "  *BA.5.x*",
    "  *BQ.1.x*",
    "  *Other*",
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
    if use_mixed:
        out.at["  *Mixed*", g] = fmt_count(d["disease"] == "Mixed")
out.at["Disease group", "Total"] = ""
out.at["Disease group", "Combination"] = ""
out.at["Disease group", "Monotherapy"] = ""
p_store["Disease group"] = p_categorical(df["disease"])
p_store["  *Haematological malignancy*"] = p_categorical(
    df["disease"] == "Haematological malignancy"
)
p_store["  *Autoimmune disease*"] = p_categorical(df["disease"] == "Autoimmune disease")
p_store["  *Transplantation*"] = p_categorical(df["disease"] == "Transplantation")
if use_mixed:
    p_store["  *Mixed*"] = p_categorical(df["disease"] == "Mixed")

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["  *Anti-CD-20*", g] = fmt_count(d["immuno_detail"] == "Anti-CD-20")
    out.at["  *Other*", g] = fmt_count(d["immuno_detail"] == "Other")
    out.at["  *None*", g] = fmt_count(d["immuno_detail"] == "None")
out.at["Immunosuppressive treatment", "Total"] = ""
out.at["Immunosuppressive treatment", "Combination"] = ""
out.at["Immunosuppressive treatment", "Monotherapy"] = ""
p_store["Immunosuppressive treatment"] = p_categorical(df["immuno3"])
p_store["  *Anti-CD-20*"] = p_categorical(df["immuno_detail"] == "Anti-CD-20")
p_store["  *Other*"] = p_categorical(df["immuno_detail"] == "Other")
p_store["  *None*"] = p_categorical(df["immuno_detail"] == "None")

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["Glucocorticoid use", g] = fmt_count(d["gc"] == "Yes")
p_store["Glucocorticoid use"] = p_categorical(df["gc"] == "Yes")

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["SARS-CoV-2 Vaccination", g] = fmt_count(d["vacc"] == "Yes")
for col in groups:
    out.at["Number of vaccine doses", col] = ""
p_store["SARS-CoV-2 Vaccination"] = p_categorical(df["vacc"] == "Yes")
p_store["Number of vaccine doses"] = p_categorical(df["dose_group"])
for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["  *0*", g] = fmt_count(d["dose_group"] == "0")
    out.at["  *1-2*", g] = fmt_count(d["dose_group"] == "1-2")
    out.at["  *3-4*", g] = fmt_count(d["dose_group"] == "3-4")
    out.at["  *≥5*", g] = fmt_count(d["dose_group"] == "≥5")
p_store["  *0*"] = p_categorical(df["dose_group"] == "0")
p_store["  *1-2*"] = p_categorical(df["dose_group"] == "1-2")
p_store["  *3-4*"] = p_categorical(df["dose_group"] == "3-4")
p_store["  *≥5*"] = p_categorical(df["dose_group"] == "≥5")

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
    out.at["  *BA.1.x*", g] = fmt_count(d["variant"] == "BA.1.x")
    out.at["  *BA.2.x*", g] = fmt_count(d["variant"] == "BA.2.x")
    out.at["  *BA.5.x*", g] = fmt_count(d["variant"] == "BA.5.x")
    out.at["  *BQ.1.x*", g] = fmt_count(d["variant"] == "BQ.1.x")
    out.at["  *Other*", g] = fmt_count(d["variant"] == "Other")
out.at["SARS-CoV-2 genotype", "Total"] = ""
out.at["SARS-CoV-2 genotype", "Combination"] = ""
out.at["SARS-CoV-2 genotype", "Monotherapy"] = ""
p_store["SARS-CoV-2 genotype"] = p_categorical(df["variant"])
p_store["  *BA.1.x*"] = p_categorical(df["variant"] == "BA.1.x")
p_store["  *BA.2.x*"] = p_categorical(df["variant"] == "BA.2.x")
p_store["  *BA.5.x*"] = p_categorical(df["variant"] == "BA.5.x")
p_store["  *BQ.1.x*"] = p_categorical(df["variant"] == "BQ.1.x")
p_store["  *Other*"] = p_categorical(df["variant"] == "Other")

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


if __name__ == "__main__":
    print(out.fillna(""))
    print("Anti-CD-20 umfasst Rituximab, Obinutuzumab, Ocrelizumab, Mosunetuzumab.")
