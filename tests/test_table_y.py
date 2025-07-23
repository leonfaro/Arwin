import importlib.util
import pathlib
import sys

path = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('data_preprocessing', path / 'data_preprocessing.py')
data_preprocessing = importlib.util.module_from_spec(spec)
sys.modules['data_preprocessing'] = data_preprocessing
spec.loader.exec_module(data_preprocessing)

spec = importlib.util.spec_from_file_location('table_y', path / 'table_y.py')
table_y = importlib.util.module_from_spec(spec)
sys.modules['data_preprocessing'] = data_preprocessing
spec.loader.exec_module(table_y)

build_table_y = table_y.build_table_y


def test_columns():
    tab = build_table_y()
    assert list(tab.columns) == [
        'Primary Cohort (n=104)',
        'Subgroup monotherapy (n=33)',
        'Subgroup combination (n=57)',
        'p-value',
    ]


def test_no_nan():
    tab = build_table_y()
    assert tab.isna().sum().sum() == 0
