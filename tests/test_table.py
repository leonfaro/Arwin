import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
out = __import__("table").out


def test_columns():
    exp = ["Total", "Combination", "Monotherapy"]
    assert out.columns[:3].tolist() == exp


def test_index_name():
    assert out.index.name == "N="


def test_rows():
    assert "Age" in out.index
    assert "Prolonged viral shedding (\u2265 14 days)" in out.index
    assert "Adverse events" in out.index
