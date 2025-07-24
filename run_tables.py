import os
from table_x import build_table_x
from table_y import build_table_y
from table_z import build_table_z
from table_B import build_table_B, COL_ERAD, COL_SURV, COL_AE_YN
import data_preprocessing
import pandas as pd
from scipy.stats import chi2_contingency, shapiro
import re


def chi_or_fisher_test(a11, a12, a21, a22):
    try:
        ex = chi2_contingency([[a11, a12], [a21, a22]])[3]
    except ValueError:
        return "Fisher"
    if (ex < 5).any():
        return "Fisher"
    return "Chi2 df=1"


def cont_test_method(v1, v2):
    v1 = pd.to_numeric(v1, errors="coerce").dropna()
    v2 = pd.to_numeric(v2, errors="coerce").dropna()
    if shapiro(v1).pvalue >= 0.05 and shapiro(v2).pvalue >= 0.05:
        s1 = v1.var(ddof=1)
        s2 = v2.var(ddof=1)
        n1 = len(v1)
        n2 = len(v2)
        df = (s1 / n1 + s2 / n2) ** 2 / ((s1 / n1) ** 2 / (n1 - 1) + (s2 / n2) ** 2 / (n2 - 1))
        return f"t-test df={int(round(df))}"
    return "Mann-Whitney-U"


def tests_table_x():
    days_m, courses_m = data_preprocessing.parse_ext(data_preprocessing.MONO[data_preprocessing.COL_EXT])
    days_c, courses_c = data_preprocessing.parse_ext(data_preprocessing.COMBO[data_preprocessing.COL_EXT])
    info = {}
    labels = [
        "Standard 5-day Paxlovid",
        "Remdesivir",
        "Molnupiravir",
        "Other antivirals",
    ]
    cols = ["flag_pax5d", "flag_rdv", "flag_mpv", "flag_other"]
    for lbl, col in zip(labels, cols):
        info[("First-line therapy\u00b9, n (%)", lbl)] = chi_or_fisher_test(
            int((data_preprocessing.COMBO[col]).sum()),
            len(data_preprocessing.COMBO) - int((data_preprocessing.COMBO[col]).sum()),
            int((data_preprocessing.MONO[col]).sum()),
            len(data_preprocessing.MONO) - int((data_preprocessing.MONO[col]).sum()),
        )
    fl_none_m = data_preprocessing.MONO[data_preprocessing.COL_OTHER].astype(str).str.lower().str.strip().eq("none")
    fl_none_c = data_preprocessing.COMBO[data_preprocessing.COL_OTHER].astype(str).str.lower().str.strip().eq("none")
    info[("First-line therapy\u00b9, n (%)", "None")] = chi_or_fisher_test(
        int(fl_none_c.sum()),
        len(fl_none_c) - int(fl_none_c.sum()),
        int(fl_none_m.sum()),
        len(fl_none_m) - int(fl_none_m.sum()),
    )
    info[("Last line therapy\u00b2, n (%)", "")] = chi_or_fisher_test(
        len(data_preprocessing.COMBO),
        0,
        0,
        len(data_preprocessing.MONO),
    )
    single_m = courses_m == 1
    multi_m = courses_m > 1
    single_c = courses_c == 1
    multi_c = courses_c > 1
    info[("Treatment courses, n (%)", "")] = chi_or_fisher_test(
        int(single_c.sum()),
        int(multi_c.sum()),
        int(single_m.sum()),
        int(multi_m.sum()),
    )
    info[("Duration", "")] = cont_test_method(days_m.dropna(), days_c.dropna())
    return info


def tests_table_y():
    info = {}
    info[("Age, median (IQR)", "")] = cont_test_method(
        data_preprocessing.MONO["age_vec"],
        data_preprocessing.COMBO["age_vec"],
    )
    info[("Female sex, n (%)", "")] = chi_or_fisher_test(
        int(data_preprocessing.COMBO["flag_female"].sum()),
        len(data_preprocessing.COMBO) - int(data_preprocessing.COMBO["flag_female"].sum()),
        int(data_preprocessing.MONO["flag_female"].sum()),
        len(data_preprocessing.MONO) - int(data_preprocessing.MONO["flag_female"].sum()),
    )
    pairs = [
        ("Hematological malignancy", "flag_malign"),
        ("Autoimmune", "flag_autoimm"),
        ("Transplantation", "flag_transpl"),
    ]
    for lbl, col in pairs:
        info[("Underlying conditions, n (%)", lbl)] = chi_or_fisher_test(
            int(data_preprocessing.COMBO[col].sum()),
            len(data_preprocessing.COMBO) - int(data_preprocessing.COMBO[col].sum()),
            int(data_preprocessing.MONO[col].sum()),
            len(data_preprocessing.MONO) - int(data_preprocessing.MONO[col].sum()),
        )
    pairs = [
        ("Anti-CD20", "flag_cd20"),
        ("CAR-T", "flag_cart"),
        ("HSCT", "flag_hsct"),
        ("None", "flag_immuno_none"),
    ]
    for lbl, col in pairs:
        info[("Immunosuppressive treatment, n (%)", lbl)] = chi_or_fisher_test(
            int(data_preprocessing.COMBO[col].sum()),
            len(data_preprocessing.COMBO) - int(data_preprocessing.COMBO[col].sum()),
            int(data_preprocessing.MONO[col].sum()),
            len(data_preprocessing.MONO) - int(data_preprocessing.MONO[col].sum()),
        )
    info[("Glucocorticoid use, n (%)", "")] = chi_or_fisher_test(
        int(data_preprocessing.COMBO["flag_gc"].sum()),
        len(data_preprocessing.COMBO) - int(data_preprocessing.COMBO["flag_gc"].sum()),
        int(data_preprocessing.MONO["flag_gc"].sum()),
        len(data_preprocessing.MONO) - int(data_preprocessing.MONO["flag_gc"].sum()),
    )
    info[("SARS-CoV-2 vaccination, n (%)", "")] = chi_or_fisher_test(
        int(data_preprocessing.COMBO["vacc_yes"].sum()),
        len(data_preprocessing.COMBO) - int(data_preprocessing.COMBO["vacc_yes"].sum()),
        int(data_preprocessing.MONO["vacc_yes"].sum()),
        len(data_preprocessing.MONO) - int(data_preprocessing.MONO["vacc_yes"].sum()),
    )
    info[("Mean Vaccination doses, n (range)", "")] = cont_test_method(
        data_preprocessing.MONO["dose_vec"],
        data_preprocessing.COMBO["dose_vec"],
    )
    info[("Thoracic CT changes, n (%)", "")] = chi_or_fisher_test(
        int(data_preprocessing.COMBO["flag_ct"].sum()),
        len(data_preprocessing.COMBO) - int(data_preprocessing.COMBO["flag_ct"].sum()),
        int(data_preprocessing.MONO["flag_ct"].sum()),
        len(data_preprocessing.MONO) - int(data_preprocessing.MONO["flag_ct"].sum()),
    )
    info[("Treatment setting\u00b9, n (%)", "")] = chi_or_fisher_test(
        int(data_preprocessing.COMBO["flag_hosp"].sum()),
        len(data_preprocessing.COMBO) - int(data_preprocessing.COMBO["flag_hosp"].sum()),
        int(data_preprocessing.MONO["flag_hosp"].sum()),
        len(data_preprocessing.MONO) - int(data_preprocessing.MONO["flag_hosp"].sum()),
    )
    return info


def tests_table_z():
    info = {}
    info[("Age, median (IQR)", "")] = cont_test_method(
        data_preprocessing.MONO["age_vec"],
        data_preprocessing.COMBO["age_vec"],
    )
    info[("Sex (female), n (%)", "")] = chi_or_fisher_test(
        int(data_preprocessing.COMBO["flag_female"].sum()),
        len(data_preprocessing.COMBO) - int(data_preprocessing.COMBO["flag_female"].sum()),
        int(data_preprocessing.MONO["flag_female"].sum()),
        len(data_preprocessing.MONO) - int(data_preprocessing.MONO["flag_female"].sum()),
    )
    for lab in [
        "Other",
        "DLBCL",
        "ALL",
        "CLL",
        "AML",
        "FL",
        "NHL",
        "MM",
        "Mixed",
    ]:
        info[("Haematological malignancy, n (%)", lab)] = chi_or_fisher_test(
            int((data_preprocessing.COMBO["heme"] == lab).sum()),
            len(data_preprocessing.COMBO) - int((data_preprocessing.COMBO["heme"] == lab).sum()),
            int((data_preprocessing.MONO["heme"] == lab).sum()),
            len(data_preprocessing.MONO) - int((data_preprocessing.MONO["heme"] == lab).sum()),
        )
    for lab in [
        "MCTD",
        "RA",
        "CREST",
        "MS",
        "SSc",
        "Colitis ulcerosa",
        "Glomerulonephritis",
        "NMDA-encephalitis",
    ]:
        info[("Autoimmune disease, n (%)", lab)] = chi_or_fisher_test(
            int((data_preprocessing.COMBO["auto"] == lab).sum()),
            len(data_preprocessing.COMBO) - int((data_preprocessing.COMBO["auto"] == lab).sum()),
            int((data_preprocessing.MONO["auto"] == lab).sum()),
            len(data_preprocessing.MONO) - int((data_preprocessing.MONO["auto"] == lab).sum()),
        )
    for lab in ["LT", "KT"]:
        info[("Transplantation, n (%)", lab)] = chi_or_fisher_test(
            int((data_preprocessing.COMBO["trans"] == lab).sum()),
            len(data_preprocessing.COMBO) - int((data_preprocessing.COMBO["trans"] == lab).sum()),
            int((data_preprocessing.MONO["trans"] == lab).sum()),
            len(data_preprocessing.MONO) - int((data_preprocessing.MONO["trans"] == lab).sum()),
        )
    for lab in [
        "Haematological malignancy",
        "Autoimmune disease",
        "Transplantation",
    ]:
        info[("Disease group, n (%)", lab)] = chi_or_fisher_test(
            int((data_preprocessing.COMBO["group"] == lab).sum()),
            len(data_preprocessing.COMBO) - int((data_preprocessing.COMBO["group"] == lab).sum()),
            int((data_preprocessing.MONO["group"] == lab).sum()),
            len(data_preprocessing.MONO) - int((data_preprocessing.MONO["group"] == lab).sum()),
        )
    for lab in ["None", "Anti-CD-20", "CAR-T"]:
        info[("Immunosuppressive treatment, n (%)", lab)] = chi_or_fisher_test(
            int((data_preprocessing.COMBO["immu"] == lab).sum()),
            len(data_preprocessing.COMBO) - int((data_preprocessing.COMBO["immu"] == lab).sum()),
            int((data_preprocessing.MONO["immu"] == lab).sum()),
            len(data_preprocessing.MONO) - int((data_preprocessing.MONO["immu"] == lab).sum()),
        )
    info[("Glucocorticoid use, n (%)", "")] = chi_or_fisher_test(
        int(data_preprocessing.COMBO["flag_gc"].sum()),
        len(data_preprocessing.COMBO) - int(data_preprocessing.COMBO["flag_gc"].sum()),
        int(data_preprocessing.MONO["flag_gc"].sum()),
        len(data_preprocessing.MONO) - int(data_preprocessing.MONO["flag_gc"].sum()),
    )
    info[("SARS-CoV-2 vaccination, n (%)", "")] = chi_or_fisher_test(
        int(data_preprocessing.COMBO["vacc_yes"].sum()),
        len(data_preprocessing.COMBO) - int(data_preprocessing.COMBO["vacc_yes"].sum()),
        int(data_preprocessing.MONO["vacc_yes"].sum()),
        len(data_preprocessing.MONO) - int(data_preprocessing.MONO["vacc_yes"].sum()),
    )
    info[("Number of vaccine doses, n (range)", "")] = cont_test_method(
        data_preprocessing.MONO["dose_vec"],
        data_preprocessing.COMBO["dose_vec"],
    )
    info[("Thoracic CT changes, n (%)", "")] = chi_or_fisher_test(
        int(data_preprocessing.COMBO["flag_ct"].sum()),
        len(data_preprocessing.COMBO) - int(data_preprocessing.COMBO["flag_ct"].sum()),
        int(data_preprocessing.MONO["flag_ct"].sum()),
        len(data_preprocessing.MONO) - int(data_preprocessing.MONO["flag_ct"].sum()),
    )
    info[("Duration of SARS-CoV-2 replication (days), median (IQR)", "")] = cont_test_method(
        data_preprocessing.MONO["rep_vec"],
        data_preprocessing.COMBO["rep_vec"],
    )
    for lab in [
        "BA.5-derived Omicron subvariant",
        "BA.2-derived Omicron subvariant",
        "BA.1-derived Omicron subvariant",
        "Other",
    ]:
        info[("SARS-CoV-2 genotype, n (%)", lab)] = chi_or_fisher_test(
            int((data_preprocessing.COMBO["geno"] == lab).sum()),
            len(data_preprocessing.COMBO) - int((data_preprocessing.COMBO["geno"] == lab).sum()),
            int((data_preprocessing.MONO["geno"] == lab).sum()),
            len(data_preprocessing.MONO) - int((data_preprocessing.MONO["geno"] == lab).sum()),
        )
    info[("Prolonged viral shedding (\u2265\u202f14\u202fdays), n (%)", "")] = chi_or_fisher_test(
        int(data_preprocessing.COMBO["flag_long"].sum()),
        len(data_preprocessing.COMBO) - int(data_preprocessing.COMBO["flag_long"].sum()),
        int(data_preprocessing.MONO["flag_long"].sum()),
        len(data_preprocessing.MONO) - int(data_preprocessing.MONO["flag_long"].sum()),
    )
    info[("Survival, n (%)", "")] = chi_or_fisher_test(
        int(data_preprocessing.COMBO["flag_surv"].sum()),
        len(data_preprocessing.COMBO) - int(data_preprocessing.COMBO["flag_surv"].sum()),
        int(data_preprocessing.MONO["flag_surv"].sum()),
        len(data_preprocessing.MONO) - int(data_preprocessing.MONO["flag_surv"].sum()),
    )
    for lab in ["None", "Thrombocytopenia", "Other"]:
        info[("Adverse events, n (%)", lab)] = chi_or_fisher_test(
            int((data_preprocessing.COMBO["adv"] == lab).sum()),
            len(data_preprocessing.COMBO) - int((data_preprocessing.COMBO["adv"] == lab).sum()),
            int((data_preprocessing.MONO["adv"] == lab).sum()),
            len(data_preprocessing.MONO) - int((data_preprocessing.MONO["adv"] == lab).sum()),
        )
    return info


def tests_table_B():
    info = {}
    c = data_preprocessing.COMBO[COL_ERAD].astype(str).str.lower().str.startswith("n")
    m = data_preprocessing.MONO[COL_ERAD].astype(str).str.lower().str.startswith("n")
    info["SARS-CoV-2 Persistence\u00b9, n (%)"] = chi_or_fisher_test(
        int(c.sum()),
        len(c) - int(c.sum()),
        int(m.sum()),
        len(m) - int(m.sum()),
    )
    c = data_preprocessing.COMBO[COL_SURV].astype(str).str.lower().str.startswith("n")
    m = data_preprocessing.MONO[COL_SURV].astype(str).str.lower().str.startswith("n")
    info["All-cause mortality\u00b2, n (%)"] = chi_or_fisher_test(
        int(c.sum()),
        len(c) - int(c.sum()),
        int(m.sum()),
        len(m) - int(m.sum()),
    )
    c = (
        data_preprocessing.COMBO[COL_ERAD].astype(str).str.lower().str.startswith("n")
        & data_preprocessing.COMBO[COL_SURV].astype(str).str.lower().str.startswith("n")
    )
    m = (
        data_preprocessing.MONO[COL_ERAD].astype(str).str.lower().str.startswith("n")
        & data_preprocessing.MONO[COL_SURV].astype(str).str.lower().str.startswith("n")
    )
    info["SARS-CoV-2-related mortality\u00b3, n (%)"] = chi_or_fisher_test(
        int(c.sum()),
        len(c) - int(c.sum()),
        int(m.sum()),
        len(m) - int(m.sum()),
    )
    c = data_preprocessing.COMBO[COL_AE_YN].astype(str).str.lower().str.startswith("y")
    m = data_preprocessing.MONO[COL_AE_YN].astype(str).str.lower().str.startswith("y")
    info["AE\u2074, n (%)"] = chi_or_fisher_test(
        int(c.sum()),
        len(c) - int(c.sum()),
        int(m.sum()),
        len(m) - int(m.sum()),
    )
    return info


def section(title, tab, tests, subrows=True):
    df = tab.copy()
    if subrows:
        if df.index.nlevels == 1:
            df.index = pd.MultiIndex.from_product([df.index, [""]])
        df.insert(0, "subrow", df.index.get_level_values(1))
        df.insert(0, "row", df.index.get_level_values(0))
        df.loc[df["subrow"] != "", "row"] = ""
        df["test"] = [tests.get(idx, "") for idx in tab.index]
    else:
        if df.index.nlevels > 1:
            df.index = df.index.get_level_values(0)
        df.insert(0, "row", df.index)
        df["test"] = [tests.get(idx, "") for idx in df.index]
    body = df.reset_index(drop=True).to_markdown(index=False)
    foot = tab.attrs.get("footnote", "")
    foot = re.sub(r"\s*(?=Abbreviations:|\d+:)", "\n", foot).strip()
    foot = "\n".join(s.strip() for s in foot.splitlines() if s.strip())
    text = "# " + title + "\n\n" + body + "\n\n" + foot + "\n\n"
    return text


def clean(path):
    if os.path.exists(path):
        os.remove(path)


def code_without_imports(path):
    lines = open(path).read().splitlines()
    i = 0
    paren = 0
    while i < len(lines):
        line = lines[i]
        strip = line.strip()
        if paren > 0:
            if "(" in line:
                paren += line.count("(")
            if ")" in line:
                paren -= line.count(")")
            i += 1
            continue
        if line.startswith("import") or line.startswith("from"):
            if line.rstrip().endswith("("):
                paren = 1
            i += 1
            continue
        if strip == "":
            i += 1
            continue
        break
    return "\n".join(lines[i:])


def main():
    t1 = build_table_x()
    t2 = build_table_y()
    t3 = build_table_z()
    t4 = build_table_B()
    m1 = tests_table_x()
    m2 = tests_table_y()
    m3 = tests_table_z()
    m4 = tests_table_B()
    data_preprocessing.export_abbreviations_md('abbreviations.md')
    out_tab = "tables.md"
    clean(out_tab)
    with open(out_tab, "w") as f:
        f.write(section("Table X. Treatment Approach", t1, m1))
        f.write(section("Table Y. Demographics and Clinical Characteristics", t2, m2))
        f.write(section("Table Z. Detailed Patient Characteristics", t3, m3))
        f.write(section("Table B. Outcomes in all cohorts", t4, m4, subrows=False))
    out_code = "code.md"
    clean(out_code)
    with open(out_code, "w") as f:
        f.write(open("data_preprocessing.py").read().rstrip() + "\n\n")
        for name in ["table_x.py", "table_y.py", "table_z.py", "table_B.py"]:
            f.write(code_without_imports(name))
            f.write("\n\n")


if __name__ == "__main__":
    main()
