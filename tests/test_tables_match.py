import pandas as pd
import pathlib
import importlib.util

path = pathlib.Path(__file__).resolve().parents[1]
exp_dir = path / 'tests' / 'expected'

spec = importlib.util.spec_from_file_location('run_tables', path / 'run_tables.py')
run_tables = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_tables)


def load_expected(name):
    return pd.read_csv(exp_dir / name, index_col=[0, 1])


def test_tables_match(tmp_path):
    run_tables.main()
    for name in ['table_a.csv', 'table_b.csv', 'table_c.csv', 'table_d.csv']:
        df_expected = load_expected(name)
        df_new = pd.read_csv(path / name, index_col=[0, 1])
        pd.testing.assert_frame_equal(df_new, df_expected)
