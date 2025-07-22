import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
tbl = __import__("table")
out = tbl.out


def test_columns():
    assert list(out.columns) == [
        "Total",
        "Combination",
        "Monotherapy",
        "p-value",
    ]


def test_n_row():
    n_row = out.loc["N="]
    assert n_row["Total"] == len(tbl.df)
    assert n_row["Combination"] + n_row["Monotherapy"] <= len(tbl.df)


def test_rows():
    assert "Age" in out.index
    assert "Prolonged viral shedding (\u226514 days)" in out.index


def test_column_access():
    src = open("table.py").read()
    assert "find_col" in src
