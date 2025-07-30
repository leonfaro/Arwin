import importlib.util
import pathlib
import sys

path = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('data_preprocessing', path / 'data_preprocessing.py')
data_preprocessing = importlib.util.module_from_spec(spec)
sys.modules['data_preprocessing'] = data_preprocessing
spec.loader.exec_module(data_preprocessing)

classify_immuno = data_preprocessing.classify_immuno
heme_subtype = data_preprocessing.heme_subtype
auto_subtype = data_preprocessing.auto_subtype


def test_classify_mixed():
    assert classify_immuno('CD20, HSCT') == 'Mixed'


def test_heme_synonym():
    assert heme_subtype('Non-Hodgkin Lymphoma') == 'NHL'
    assert heme_subtype('FCL') == 'FL'


def test_auto_synonym():
    assert auto_subtype('rheum. arthritis') == 'RA'
