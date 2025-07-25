import importlib.util
import pathlib
import sys

path = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(path))
spec = importlib.util.spec_from_file_location('run_tables', path / 'run_tables.py')
run_tables = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_tables)


def test_run_tables_output():
    for f in ['code.md', 'tables.md']:
        p = path / f
        if p.exists():
            p.unlink()
    run_tables.main()
    assert (path / 'code.md').exists()
    assert (path / 'tables.md').exists()
