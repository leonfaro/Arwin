import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
out = __import__("table").out


def test_columns():
    assert list(out.columns) == [
        "Total",
        "Combination",
        "Monotherapy",
        "p-Value",
        "q-Value",
        "Sig",
    ]


def test_index_name():
    assert out.index.name == "N="


def test_rows():
    assert "Age" in out.index
    assert "Prolonged viral shedding (\u226514 days)" in out.index


def test_column_access():
    src = open("table.py").read()
    assert "find_col" in src
