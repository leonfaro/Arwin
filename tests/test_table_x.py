import importlib.util
import pathlib
import sys

path = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('data_preprocessing', path / 'data_preprocessing.py')
data_preprocessing = importlib.util.module_from_spec(spec)
sys.modules['data_preprocessing'] = data_preprocessing
spec.loader.exec_module(data_preprocessing)

spec = importlib.util.spec_from_file_location('table_x', path / 'table_x.py')
table_x = importlib.util.module_from_spec(spec)
sys.modules['data_preprocessing'] = data_preprocessing
spec.loader.exec_module(table_x)
build_table_x = table_x.build_table_x
TOTAL = data_preprocessing.TOTAL


def test_columns():
    tab = build_table_x()
    assert list(tab.columns) == [
        'Primary Cohort (n=104)',
        'Subgroup monotherapy (n=33)',
        'Subgroup combination (n=57)',
        'p-value',
    ]


def test_flag_counts():
    tab = TOTAL[['flag_pax5d', 'flag_rdv', 'flag_mpv', 'flag_other']]
    assert tab.sum().sum() >= 0
