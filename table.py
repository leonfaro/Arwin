import pandas as pd
import numpy as np
import re


def load_file(label, path):
    df_tmp = pd.read_excel(path)
    df_tmp["group"] = label
    df_tmp["source_sheet"] = label
    col = None
    for c in df_tmp.columns:
        if str(c).lower().startswith("2nd line treatment form of therapy"):
            col = c
            break
    if col is not None:
        df_tmp["therapy"] = (
            df_tmp[col]
            .str.lower()
            .str[0]
            .map({"c": "Combination", "m": "Monotherapy"})
            .fillna("Unknown")
        )
    else:
        df_tmp["therapy"] = label
    return df_tmp


df_total = load_file("Total", "Total.xlsx")
df_combo = load_file("Combination", "Combination.xlsx")
df_mono = load_file("Monotherapy", "Monotherapy.xlsx")
df = df_total.copy()


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
    therapy = therapy.fillna("Unknown")
else:
    def infer(x):
        s = str(x)
        if "combo" in s.lower():
            return "Combination"
        if "mono" in s.lower():
            return "Monotherapy"
        return np.nan
    therapy = df["source_sheet"].map(infer).fillna("Unknown")
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
    s = x.upper()
    a = "AUTO" in s
    m = "MALIGN" in s
    t = "TRANSPLANT" in s
    if sum([a, m, t]) > 1:
        return "Mixed"
    if a:
        return "Autoimmune disease"
    if m:
        return "Haematological malignancy"
    if t:
        return "Transplantation"
    return "Unknown"


def group_immuno_detail(x):
    if not isinstance(x, str) or not x.strip():
        return "None"
    s = x.lower()
    if any(k in s for k in ("ritux", "obinu", "ocrel", "mosune", "cd-20")):
        return "Anti-CD-20"
    if "none" in s or "no is" in s:
        return "None"
    return "Other"


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
    if not s:
        return "Unknown"
    if any(k in s for k in ("pdn", "pred", "dxa", "dexa", "meth")):
        return "Yes"
    return "Yes"


def parse_vacc(x):
    if not isinstance(x, str):
        return ("Unknown", np.nan)
    s = x.lower().strip()
    m = re.search(r"(\d+)", s)
    dose = float(m.group(1)) if m else 0.0
    if s.startswith("n") or dose == 0:
        return ("No", dose)
    if dose >= 1:
        return ("Yes", dose)
    return ("Unknown", np.nan)


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


def group_ct(x):
    if not isinstance(x, str):
        return "Unknown"
    s = x.lower().strip()
    if re.search(r"y|yes|opa|ggo|infilt", s):
        return "Yes"
    if re.search(r"n|no|normal", s):
        return "No"
    return "Unknown"


def parse_rep(x):
    if isinstance(x, (int, float)) and not pd.isna(x):
        return float(x)
    if not isinstance(x, str):
        return np.nan
    m = re.search(r"(\d+)", x)
    return float(m.group(1)) if m else np.nan


def group_variant(x):
    if not isinstance(x, str):
        return "Unknown"
    s = x.upper().strip()
    if re.search(r"BQ\.?1", s):
        return "BQ.1.x"
    if re.search(r"BA\.?5", s):
        return "BA.5.x"
    if re.search(r"BA\.?4", s):
        return "BA.4.x"
    if re.search(r"BA\.?2", s):
        return "BA.2.x"
    if re.search(r"BA\.?1", s):
        return "BA.1.x"
    if re.search(r"XBB", s):
        return "XBB.x"
    if re.search(r"JN", s):
        return "JN.x"
    return "Other"


def flag_survival(x):
    if not isinstance(x, str):
        return "Unknown"
    s = x.lower().strip()
    if re.search(r"^(alive|yes|1)", s):
        return "Yes"
    if re.search(r"^(dead|no|0)", s):
        return "No"
    return "Unknown"


def group_adv(a, t):
    a_s = str(a).lower().strip()
    t_s = str(t).lower()
    if a_s.startswith("y"):
        if "thrombocyt" in t_s:
            return "Thrombocytopenia"
        return "Other"
    if a_s.startswith("n") or a_s in {"none", ""}:
        return "None"
    return "Unknown"


def transform(d):
    d["disease"] = d[col_disease].map(group_disease)
    d["immuno_detail"] = d[col_base].map(group_immuno_detail)
    d["immuno3"] = d["immuno_detail"].map(
        lambda x: "Anti-CD-20" if x == "Anti-CD-20" else ("None" if x == "None" else "Other")
    )
    d["gc"] = d[col_gc].map(flag_gc)
    vacc = d[col_vacc].map(parse_vacc)
    d["vacc"] = vacc.map(lambda x: x[0])
    d["doses"] = vacc.map(lambda x: x[1])
    d["dose_group"] = d["doses"].map(group_dose)
    d["ct"] = d[col_ct].map(group_ct)
    d["rep"] = d[col_rep].map(parse_rep)
    d["variant"] = d[col_gen].map(group_variant)
    d["prolonged"] = d["rep"].map(lambda x: np.nan if pd.isna(x) else x >= 14)
    d["survival"] = d[col_surv].map(flag_survival)
    d["adverse"] = d.apply(lambda r: group_adv(r[col_adv], r[col_adv_type]), axis=1)
    return d


df_total = transform(df_total)
df_combo = transform(df_combo)
df_mono = transform(df_mono)
group_map = {"Total": df_total, "Combination": df_combo, "Monotherapy": df_mono}
df = df_total


def fmt_num(x, typ):
    if typ == "mean":
        return f"{x.mean():.1f} ± {x.std():.1f}"
    return f"{int(x.median())} ({int(x.quantile(0.25))}-{int(x.quantile(0.75))})"


def fmt_count(mask, denom=None):
    n = mask.sum()
    d = len(mask) if denom is None else denom
    if d == 0:
        return "0 (0.0%)"
    return f"{n} ({n / d * 100:.1f}%)"


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
var_order = ["BA.1.x", "BA.2.x", "BA.4.x", "BA.5.x", "BQ.1.x", "XBB.x", "JN.x", "Other"]
rows += [f"  *{i}*" for i in unique_order(df["variant"].unique(), var_order)]
rows += ["Prolonged viral shedding (≥14 days)", "Survival", "Adverse events"]
ae_order = ["None", "Thrombocytopenia", "Other"]
rows += [f"  *{i}*" for i in unique_order(df["adverse"].unique(), ae_order)]

groups = ["Total", "Combination", "Monotherapy"]
cols = groups
out = pd.DataFrame(index=rows, columns=cols)
out.loc["N=", "Total"] = len(df_total)
out.loc["N=", "Combination"] = len(df_combo)
out.loc["N=", "Monotherapy"] = len(df_mono)

for g in groups:
    d = group_map[g]
    out.at["Age", g] = fmt_num(d[col_age], "median")

female = df[col_sex].map(is_female)
for g in groups:
    d = group_map[g]
    out.at["Sex (female)", g] = fmt_count(female.loc[d.index].fillna(False))

for g in groups:
    d = group_map[g]
    for cat in unique_order(df["disease"].unique(), disease_order):
        out.at[f"  *{cat}*", g] = fmt_count(d["disease"] == cat)
out.at["Disease group", "Total"] = ""
out.at["Disease group", "Combination"] = ""
out.at["Disease group", "Monotherapy"] = ""

for g in groups:
    d = group_map[g]
    for cat in unique_order(df["immuno_detail"].unique(), immuno_order):
        out.at[f"  *{cat}*", g] = fmt_count(d["immuno_detail"] == cat)
out.at["Immunosuppressive treatment", "Total"] = ""
out.at["Immunosuppressive treatment", "Combination"] = ""
out.at["Immunosuppressive treatment", "Monotherapy"] = ""

for g in groups:
    d = group_map[g]
    out.at["Glucocorticoid use", g] = fmt_count(d["gc"] == "Yes")

for g in groups:
    d = group_map[g]
    out.at["SARS-CoV-2 Vaccination", g] = fmt_count(d["vacc"] == "Yes")
for g in groups:
    out.at["Number of vaccine doses", g] = ""
for g in groups:
    d = group_map[g]
    for cat in unique_order(df["dose_group"].dropna().unique(), dose_order):
        out.at[f"  *{cat}*", g] = fmt_count(d["dose_group"] == cat)
for g in groups:
    d = group_map[g]
    out.at["Thoracic CT changes", g] = fmt_count(d["ct"] == "Yes")

mode_rep = "median"
for g in groups:
    d = group_map[g]
    out.at["Duration of SARS-CoV-2 replication (days)", g] = fmt_num(d["rep"], mode_rep)

for g in groups:
    d = group_map[g]
    for cat in unique_order(df["variant"].unique(), var_order):
        out.at[f"  *{cat}*", g] = fmt_count(d["variant"] == cat)
out.at["SARS-CoV-2 genotype", "Total"] = ""
out.at["SARS-CoV-2 genotype", "Combination"] = ""
out.at["SARS-CoV-2 genotype", "Monotherapy"] = ""

for g in groups:
    d = group_map[g]
    out.at["Prolonged viral shedding (≥14 days)", g] = fmt_count(d["prolonged"])

for g in groups:
    d = group_map[g]
    out.at["Survival", g] = fmt_count(d["survival"] == "Yes")

for g in groups:
    d = group_map[g]
    for cat in unique_order(df["adverse"].unique(), ae_order):
        name = "None (AE)" if cat == "None" else cat
        out.at[f"  *{name}*", g] = fmt_count(d["adverse"] == cat)
out.at["Adverse events", "Total"] = ""
out.at["Adverse events", "Combination"] = ""
out.at["Adverse events", "Monotherapy"] = ""

if __name__ == "__main__":
    print(out.fillna(""))
    print("Anti-CD-20 umfasst Rituximab, Obinutuzumab, Ocrelizumab, Mosunetuzumab.")
