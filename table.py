import pandas as pd
import numpy as np
from scipy.stats import fisher_exact, chi2_contingency, mannwhitneyu, shapiro, ttest_ind
from statsmodels.stats.multitest import multipletests
import re

xls = pd.ExcelFile("Data.xlsx")
relevant = [s for s in xls.sheet_names if re.search("combination|monotherapy", s, re.I)]
frames = [pd.read_excel(xls, s).assign(source_sheet=s) for s in relevant]
df = pd.concat(frames, ignore_index=True)


def find_col(df, *keywords):
    kws = [k.lower() for k in keywords]
    for c in df.columns:
        s = str(c).lower()
        if all(k in s for k in kws):
            return c
    raise KeyError(",".join(keywords))


col_therapy = None
for c in df.columns:
    if str(c).lower().startswith("2nd line treatment form of therapy"):
        col_therapy = c
        break
if col_therapy is not None:
    therapy = df[col_therapy].str.lower().str[0].map({"c": "Combination", "m": "Monotherapy"})
else:
    def infer(x):
        s = str(x)
        if "combo" in s.lower():
            return "Combination"
        if "mono" in s.lower():
            return "Monotherapy"
        return np.nan
    therapy = df["source_sheet"].map(infer)
    df[col_therapy] = ""
df["therapy"] = therapy

col_sex = find_col(df, "sex")
col_age = find_col(df, "age")
col_disease = find_col(df, "baseline disease cohort")
col_base = find_col(df, "baseline therapy")
col_vacc = find_col(df, "vaccination")
col_gen = find_col(df, "sars-cov-2", "genotype")
col_ct = find_col(df, "ct", "lung")
col_rep = find_col(df, "replication")
col_gc = find_col(df, "glucocorticosteroid")
col_adv = find_col(df, "any adverse events")
col_adv_type = find_col(df, "type of adverse")
col_surv = find_col(df, "survival outcome")

mandatory = [col_sex, col_age, col_disease, col_base, col_vacc,
             col_gen, col_ct, col_rep, col_gc, col_adv, col_adv_type, col_surv]
missing = [c for c in mandatory if c not in df.columns]
print(len(df), len(df.columns), df["therapy"].value_counts().to_dict(), missing)
if missing:
    raise SystemExit("missing columns")


def group_disease(x):
    if not isinstance(x, str):
        return "Unknown"
    tokens = set(i.strip() for i in re.split(r"[ /,;]", x.upper()) if i.strip())
    a = "A" in tokens
    m = "M" in tokens
    t = "T" in tokens
    if sum([a, m, t]) > 1:
        return "Mixed"
    if a:
        return "Autoimmune disease"
    if m:
        return "Haematological malignancy"
    if t:
        return "Transplantation"
    return "Unknown"


df["disease"] = df[col_disease].map(group_disease)


def group_immuno_detail(x):
    if not isinstance(x, str) or not x.strip():
        return "None"
    s = x.lower()
    if re.search("cd20|umab", s):
        return "Anti-CD-20"
    if "none" in s or "no is" in s:
        return "None"
    return "Other"


df["immuno_detail"] = df[col_base].map(group_immuno_detail)
df["immuno3"] = df["immuno_detail"].map(lambda x: "Anti-CD-20" if x ==
                                        "Anti-CD-20" else ("None" if x == "None" else "Other"))


def is_female(x):
    s = str(x).lower().strip()
    if s in {"f", "female", "w", "weiblich", "1"}:
        return True
    if s in {"m", "male", "0", "mann", "männlich"}:
        return False
    return np.nan


def flag_gc(x):
    if not isinstance(x, str):
        return "Unknown"
    s = x.lower().strip()
    if re.search(r"^(n|no|0)", s):
        return "No"
    if re.search(r"^(y|yes|1|pred)", s):
        return "Yes"
    return "Unknown"


df["gc"] = df[col_gc].map(flag_gc)


def parse_vacc(x):
    if not isinstance(x, str):
        return ("Unknown", np.nan)
    s = x.lower().strip()
    if re.search(r"^(n|no)", s):
        return ("No", 0.0)
    if re.search(r"^(y|yes|vacc)", s):
        clean = re.sub(r"[^0-9]", " ", s)
        m = re.findall(r"\d+", clean)
        return ("Yes", float(m[0]) if m else np.nan)
    return ("Unknown", np.nan)


vacc = df[col_vacc].map(parse_vacc)
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
    if re.search(r"y|yes|positive|opa", s):
        return "Yes"
    if re.search(r"n|no|normal|neg", s):
        return "No"
    return "Unknown"


df["ct"] = df[col_ct].map(group_ct)


def parse_rep(x):
    if isinstance(x, (int, float)) and not pd.isna(x):
        return float(x)
    if not isinstance(x, str):
        return np.nan
    m = re.search(r"(\d+)", x)
    return float(m.group(1)) if m else np.nan


df["rep"] = df[col_rep].map(parse_rep)


def group_variant(x):
    if not isinstance(x, str):
        return "Unknown"
    s = x.upper().strip()
    if re.search(r"BQ\.?1", s):
        return "BQ.1.x"
    if re.search(r"BA\.?5", s):
        return "BA.5.x"
    if re.search(r"BA\.?2", s):
        return "BA.2.x"
    if re.search(r"BA\.?1", s):
        return "BA.1.x"
    return "Other"


df["variant"] = df[col_gen].map(group_variant)
df["prolonged"] = df["rep"].map(lambda x: np.nan if pd.isna(x) else x >= 14)


def flag_survival(x):
    if not isinstance(x, str):
        return "Unknown"
    s = x.lower().strip()
    if re.search(r"^(alive|yes|1)", s):
        return "Yes"
    if re.search(r"^(dead|no|0)", s):
        return "No"
    return "Unknown"


df["survival"] = df[col_surv].map(flag_survival)


def group_adv(a, t):
    a_s = str(a).lower().strip()
    t_s = str(t).lower().strip()
    if not a_s:
        a_s = "y" if t_s else ""
    if a_s.startswith("y"):
        if re.search("thrombocytopenia|platelet", t_s):
            return "Thrombocytopenia"
        return "Other"
    if a_s.startswith("n"):
        return "None"
    return "Unknown"


df["adverse"] = df.apply(lambda r: group_adv(r[col_adv], r[col_adv_type]), axis=1)


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
    if series.nunique() < 2 or df["therapy"].nunique() < 2:
        return np.nan
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
    normal = n1 >= 30 and n2 >= 30 and (n1 < 3 or shapiro(g1).pvalue > 0.05) and (n2 < 3 or shapiro(g2).pvalue > 0.05)
    if normal:
        return ttest_ind(g1, g2, equal_var=False).pvalue, "mean"
    return mannwhitneyu(g1, g2, alternative="two-sided").pvalue, "median"


def fmt_num(x, typ):
    if typ == "mean":
        return f"{x.mean():.1f} ± {x.std():.1f}"
    return f"{int(x.median())} ({int(x.quantile(0.25))}-{int(x.quantile(0.75))})"


def fmt_count(mask):
    n = mask.sum()
    if n == 0:
        return "0 (0.0%)"
    return f"{n} ({mask.mean() * 100:.1f}%)"


def unique_order(seq, order):
    return [i for i in order if i in seq]


rows = ["N=", "Age", "Sex (female)", "Disease group"]
disease_order = ["Haematological malignancy", "Autoimmune disease", "Transplantation", "Mixed"]
rows += [f"  *{i}*" for i in unique_order(df["disease"].unique(), disease_order)]
rows += ["Immunosuppressive treatment"]
immuno_order = ["Anti-CD-20", "Other", "None"]
rows += [f"  *{i}*" for i in unique_order(df["immuno_detail"].unique(), immuno_order)]
rows += ["Glucocorticoid use", "SARS-CoV-2 Vaccination", "Number of vaccine doses"]
dose_order = ["0", "1-2", "3-4", "≥5"]
rows += [f"  *{i}*" for i in unique_order(df["dose_group"].dropna().unique(), dose_order)]
rows += ["Thoracic CT changes", "Duration of SARS-CoV-2 replication (days)", "SARS-CoV-2 genotype"]
var_order = ["BA.1.x", "BA.2.x", "BA.5.x", "BQ.1.x", "Other"]
rows += [f"  *{i}*" for i in unique_order(df["variant"].unique(), var_order)]
rows += ["Prolonged viral shedding (≥14 days)", "Survival", "Adverse events"]
ae_order = ["None", "Thrombocytopenia", "Other"]
rows += [f"  *{i}*" for i in unique_order(df["adverse"].unique(), ae_order)]

groups = ["Total", "Combination", "Monotherapy"]
cols = groups + ["p-Value", "q-Value", "Sig"]
out = pd.DataFrame(index=rows, columns=cols)
out.loc["N=", "Total"] = len(df)
out.loc["N=", "Combination"] = (df["therapy"] == "Combination").sum()
out.loc["N=", "Monotherapy"] = (df["therapy"] == "Monotherapy").sum()

p_store = {}

p_store["Age"], mode_age = p_continuous(df[col_age])
for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["Age", g] = fmt_num(d[col_age], mode_age)

female = df[col_sex].map(is_female)
mask_comb = (df["therapy"] == "Combination") & female
mask_mono = (df["therapy"] == "Monotherapy") & female
out.at["Sex (female)", "Combination"] = fmt_count(mask_comb)
out.at["Sex (female)", "Monotherapy"] = fmt_count(mask_mono)
out.at["Sex (female)", "Total"] = fmt_count(female)
p_store["Sex (female)"] = p_categorical(female)

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    for cat in unique_order(df["disease"].unique(), disease_order):
        out.at[f"  *{cat}*", g] = fmt_count(d["disease"] == cat)
out.at["Disease group", "Total"] = ""
out.at["Disease group", "Combination"] = ""
out.at["Disease group", "Monotherapy"] = ""
p_store["Disease group"] = p_categorical(df["disease"])
for cat in unique_order(df["disease"].unique(), disease_order):
    p_store[f"  *{cat}*"] = p_categorical(df["disease"] == cat)

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    for cat in unique_order(df["immuno_detail"].unique(), immuno_order):
        out.at[f"  *{cat}*", g] = fmt_count(d["immuno_detail"] == cat)
out.at["Immunosuppressive treatment", "Total"] = ""
out.at["Immunosuppressive treatment", "Combination"] = ""
out.at["Immunosuppressive treatment", "Monotherapy"] = ""
p_store["Immunosuppressive treatment"] = p_categorical(df["immuno3"])
for cat in unique_order(df["immuno_detail"].unique(), immuno_order):
    p_store[f"  *{cat}*"] = p_categorical(df["immuno_detail"] == cat)

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["Glucocorticoid use", g] = fmt_count(d["gc"] == "Yes")
p_store["Glucocorticoid use"] = p_categorical(df["gc"] == "Yes")

for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    out.at["SARS-CoV-2 Vaccination", g] = fmt_count(d["vacc"] == "Yes")
for g in groups:
    out.at["Number of vaccine doses", g] = ""
p_store["SARS-CoV-2 Vaccination"] = p_categorical(df["vacc"] == "Yes")
p_store["Number of vaccine doses"] = p_categorical(df["dose_group"])
for g in groups:
    d = df if g == "Total" else df[df["therapy"] == g]
    for cat in unique_order(df["dose_group"].dropna().unique(), dose_order):
        out.at[f"  *{cat}*", g] = fmt_count(d["dose_group"] == cat)
for cat in unique_order(df["dose_group"].dropna().unique(), dose_order):
    p_store[f"  *{cat}*"] = p_categorical(df["dose_group"] == cat)

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
    for cat in unique_order(df["variant"].unique(), var_order):
        out.at[f"  *{cat}*", g] = fmt_count(d["variant"] == cat)
out.at["SARS-CoV-2 genotype", "Total"] = ""
out.at["SARS-CoV-2 genotype", "Combination"] = ""
out.at["SARS-CoV-2 genotype", "Monotherapy"] = ""
p_store["SARS-CoV-2 genotype"] = p_categorical(df["variant"])
for cat in unique_order(df["variant"].unique(), var_order):
    p_store[f"  *{cat}*"] = p_categorical(df["variant"] == cat)

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
    for cat in unique_order(df["adverse"].unique(), ae_order):
        name = "None (AE)" if cat == "None" else cat
        out.at[f"  *{name}*", g] = fmt_count(d["adverse"] == cat)
out.at["Adverse events", "Total"] = ""
out.at["Adverse events", "Combination"] = ""
out.at["Adverse events", "Monotherapy"] = ""
p_store["Adverse events"] = p_categorical(df["adverse"])
for cat in unique_order(df["adverse"].unique(), ae_order):
    name = "None (AE)" if cat == "None" else cat
    p_store[f"  *{name}*"] = p_categorical(df["adverse"] == cat)

pvals = pd.Series(p_store)
mask = pvals.notna()
qs = pd.Series(index=pvals.index, dtype=float)
qs[mask] = multipletests(pvals[mask], method="fdr_bh")[1]

out["p-Value"] = pvals.apply(lambda x: "<0.001" if x < 0.001 else f"{x:.3f}" if pd.notna(x) else "")
out["q-Value"] = qs.apply(lambda x: "" if pd.isna(x) else ("<0.001" if x < 0.001 else f"{x:.3f}"))
out["Sig"] = qs.apply(lambda x: "***" if pd.notna(x) and x <= 0.001 else ("**" if pd.notna(x)
                      and x <= 0.01 else ("*" if pd.notna(x) and x <= 0.05 else "")))

if __name__ == "__main__":
    print(out.fillna(""))
    print("Anti-CD-20 umfasst Rituximab, Obinutuzumab, Ocrelizumab, Mosunetuzumab.")
