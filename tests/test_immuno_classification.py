import pytest
from data_preprocessing import classify_immuno

CASES = {
    'CD20': 'Anti-CD20',
    'rituximab': 'Anti-CD20',
    'ocrelizumab': 'Anti-CD20',
    'obinutuzumab': 'Anti-CD20',
    'ofatumumab': 'Anti-CD20',
    'car-t': 'CAR-T',
    'car t': 'CAR-T',
    'cart': 'CAR-T',
    'chimeric antigen receptor': 'CAR-T',
    'tisa-cel': 'CAR-T',
    'axi-cel': 'CAR-T',
    'hsct': 'HSCT',
    'hematopoietic stem cell': 'HSCT',
    'stem cell transplant': 'HSCT',
    'bone marrow': 'HSCT',
    'none': 'None',
    '': 'None',
    'no antiviral': 'None',
    'rituximab and car-t': 'Mixed',
    'unknown therapy': 'Other'
}


@pytest.mark.parametrize('label,expected', CASES.items())
def test_classify_immuno(label, expected):
    assert classify_immuno(label) == expected
