import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
out = __import__("table").out


def test_pvalue_column():
    assert "p-Value" in out.columns
    assert out.at["Age", "p-Value"] != ""
