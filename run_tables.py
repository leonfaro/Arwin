import os
from table_x import build_table_x
from table_y import build_table_y
from table_z import build_table_z
import data_preprocessing


def section(title, tab):
    df = tab.copy()
    df.insert(0, "subrow", df.index.get_level_values(1))
    df.insert(0, "row", df.index.get_level_values(0))
    df.loc[df["subrow"] != "", "row"] = ""
    body = df.reset_index(drop=True).to_markdown(index=False)
    text = "# " + title + "\n\n" + body + "\n\n" + tab.attrs.get("footnote", "") + "\n\n"
    return text


def clean(path):
    if os.path.exists(path):
        os.remove(path)


def code_without_imports(path):
    lines = open(path).read().splitlines()
    i = 0
    while i < len(lines) and (lines[i].startswith("import") or lines[i].startswith("from")):
        i += 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    return "\n".join(lines[i:])


def main():
    t1 = build_table_x()
    t2 = build_table_y()
    t3 = build_table_z()
    data_preprocessing.export_abbreviations_md('abbreviations.md')
    out_tab = "tables.md"
    clean(out_tab)
    with open(out_tab, "w") as f:
        f.write(section("Table X", t1))
        f.write(section("Table Y", t2))
        f.write(section("Table Z", t3))
    out_code = "code.md"
    clean(out_code)
    with open(out_code, "w") as f:
        f.write("## data_preprocessing.py\n\n```python\n")
        f.write(open("data_preprocessing.py").read())
        f.write("\n```\n\n")
        for name in ["table_x.py", "table_y.py", "table_z.py"]:
            f.write(f"## {name}\n\n```python\n")
            f.write(code_without_imports(name))
            f.write("\n```\n\n")


if __name__ == "__main__":
    main()
