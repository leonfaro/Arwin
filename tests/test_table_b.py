import importlib.util
import pathlib
import sys

path = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('data_preprocessing', path / 'data_preprocessing.py')
data_preprocessing = importlib.util.module_from_spec(spec)
sys.modules['data_preprocessing'] = data_preprocessing
spec.loader.exec_module(data_preprocessing)

spec = importlib.util.spec_from_file_location('table_b', path / 'table_b.py')
table_b = importlib.util.module_from_spec(spec)
sys.modules['data_preprocessing'] = data_preprocessing
spec.loader.exec_module(table_b)

build_table_b = table_b.build_table_b


def test_columns():
    tab = build_table_b()
    assert list(tab.columns) == [
        'Total',
        'Monotherapy',
        'Combination',
        'p-value',
    ]


def test_no_nan():
    tab = build_table_b()
    assert tab.isna().sum().sum() == 0
