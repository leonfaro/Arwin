import os
from table_a import build_table_a
from table_b import build_table_b
from table_c import build_table_c
from table_d import build_table_d, COL_ERAD, COL_SURV, COL_AE_YN
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


def tests_table_a():
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


def tests_table_b():
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


def tests_table_c():
    info = {}
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
    info[("Duration of SARS-CoV-2 replication (days), median (IQR)", "")] = cont_test_method(
        data_preprocessing.MONO["rep_vec"],
        data_preprocessing.COMBO["rep_vec"],
    )
    for lab in [
        "BA.5",
        "BA.2",
        "BA.1",
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


def tests_table_d():
    info = {}
    c = data_preprocessing.COMBO[COL_ERAD].map(data_preprocessing.parse_yn).eq(False)
    m = data_preprocessing.MONO[COL_ERAD].map(data_preprocessing.parse_yn).eq(False)
    info["SARS-CoV-2 Persistence\u00b9, n (%)"] = chi_or_fisher_test(
        int(c.sum()),
        len(c) - int(c.sum()),
        int(m.sum()),
        len(m) - int(m.sum()),
    )
    c = data_preprocessing.COMBO[COL_SURV].map(data_preprocessing.parse_yn).eq(False)
    m = data_preprocessing.MONO[COL_SURV].map(data_preprocessing.parse_yn).eq(False)
    info["All-cause mortality\u00b2, n (%)"] = chi_or_fisher_test(
        int(c.sum()),
        len(c) - int(c.sum()),
        int(m.sum()),
        len(m) - int(m.sum()),
    )
    c = (
        data_preprocessing.COMBO[COL_ERAD].map(data_preprocessing.parse_yn).eq(False)
        & data_preprocessing.COMBO[COL_SURV].map(data_preprocessing.parse_yn).eq(False)
    )
    m = (
        data_preprocessing.MONO[COL_ERAD].map(data_preprocessing.parse_yn).eq(False)
        & data_preprocessing.MONO[COL_SURV].map(data_preprocessing.parse_yn).eq(False)
    )
    info["SARS-CoV-2-related mortality\u00b3, n (%)"] = chi_or_fisher_test(
        int(c.sum()),
        len(c) - int(c.sum()),
        int(m.sum()),
        len(m) - int(m.sum()),
    )
    c = data_preprocessing.COMBO[COL_AE_YN].map(data_preprocessing.parse_yn).eq(True)
    m = data_preprocessing.MONO[COL_AE_YN].map(data_preprocessing.parse_yn).eq(True)
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
    foot = tab.attrs.get("footnote", "").strip()
    foot = re.sub(r"\s*(?=\d+:)", "\n", foot)
    foot = "\n".join(s.strip() for s in foot.splitlines() if s.strip())
    text = "# " + title + "\n\n" + body + "\n\n" + foot + "\n\n"
    return text


def section_no_test(title, tab, subrows=True):
    df = tab.copy()
    if subrows:
        if df.index.nlevels == 1:
            df.index = pd.MultiIndex.from_product([df.index, [""]])
        df.insert(0, "subrow", df.index.get_level_values(1))
        df.insert(0, "row", df.index.get_level_values(0))
        df.loc[df["subrow"] != "", "row"] = ""
    else:
        if df.index.nlevels > 1:
            df.index = df.index.get_level_values(0)
        df.insert(0, "row", df.index)
    body = df.reset_index(drop=True).to_markdown(index=False)
    foot = tab.attrs.get("footnote", "").strip()
    foot = re.sub(r"\s*(?=\d+:)", "\n", foot)
    foot = "\n".join(
        s.strip() for s in foot.splitlines() if s.strip() and not s.startswith("Abbreviations")
    )
    foot = "  \n".join(f"{s}  " for s in foot.splitlines())
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
    t1 = build_table_a()
    t2 = build_table_b()
    t3 = build_table_c()
    t4 = build_table_d()
    m1 = tests_table_a()
    m2 = tests_table_b()
    m3 = tests_table_c()
    m4 = tests_table_d()
    data_preprocessing.export_abbreviations_md('abbreviations.md')
    out_tab = "tables.md"
    clean(out_tab)
    with open(out_tab, "w") as f:
        f.write(section("Table A. Treatment Approach", t1, m1))
        f.write(section("Table B. Demographics and Clinical Characteristics", t2, m2))
        f.write(section("Table C. Detailed Patient Characteristics", t3, m3))
        f.write(section("Table D. Outcomes in all cohorts", t4, m4, subrows=False))
    out_nt = "table_no_test.md"
    clean(out_nt)
    with open(out_nt, "w") as f:
        f.write(section_no_test("Table A. Treatment Approach", t1))
        f.write("\\newpage\n")
        f.write(section_no_test("Table B. Demographics and Clinical Characteristics", t2))
        f.write("\\newpage\n")
        f.write(section_no_test("Table C. Detailed Patient Characteristics", t3))
        f.write("   \n")
        f.write(section_no_test("Table D. Outcomes in all cohorts", t4, subrows=False))
    out_code = "code.md"
    clean(out_code)
    with open(out_code, "w") as f:
        f.write(open("data_preprocessing.py").read().rstrip() + "\n\n")
        for name in ["table_a.py", "table_b.py", "table_c.py", "table_d.py"]:
            f.write(code_without_imports(name))
            f.write("\n\n")


if __name__ == "__main__":
    main()
