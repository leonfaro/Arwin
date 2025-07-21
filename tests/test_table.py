import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
out = __import__("table_v2").out


def test_columns():
    assert list(out.columns) == ["Total", "Combination", "Monotherapy"]


def test_index_name():
    assert out.index.name == "N="


def test_rows():
    assert "Age" in out.index
    assert "Prolonged viral shedding (\u2265 14 days)" in out.index


def test_column_access():
    src = open("table.py").read()
    assert "any previous NMV-r treatment …" in src
