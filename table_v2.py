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
    fill(df, "  *BA.5-derived Omicron subvariant*", df["variant"] == "BA.5-derived Omicron subvariant", col)
    fill(df, "  *BA.2-derived Omicron subvariant*", df["variant"] == "BA.2-derived Omicron subvariant", col)
    fill(df, "  *BA.1-derived Omicron subvariant*", df["variant"] == "BA.1-derived Omicron subvariant", col)
    fill(df, "  *Other*", df["variant"] == "Other", col)
    fill(df, "Prolonged viral shedding (≥ 14 days)", df["prolonged"], col)

if __name__ == "__main__":
    print(out.fillna(""))

