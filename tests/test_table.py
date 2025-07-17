import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
out = __import__("table").out


def test_pvalue_column():
    assert "p-Value" in out.columns
    assert out.at["Age", "p-Value"] != ""


def test_additional_pvalues():
    rows = [
        "  *BA.1-derived Omicron subvariant*",
        "Prolonged viral shedding (≥14 days)",
        "Survival",
        "Adverse events",
    ]
    for r in rows:
        assert out.at[r, "p-Value"] != ""
