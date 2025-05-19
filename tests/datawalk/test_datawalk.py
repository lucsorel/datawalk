from datawalk import Walk

from pytest import mark, raises

class Pet:
    def __init__(self, name: str):
        self.name = name

data = {
    'name': 'Suzie Q',
    'org': {
        'title': 'Datawalk',
        'address': {'country': 'France'},
        'phones': ['01 23 45 67 89', '02 13 46 58 79'],
        (666, 'ev/l'): 'hashable key'
    },
    'friends': [
        {'name': 'Frankie Manning'},
        {'name': 'Harry Cover'},
        {'name': 'Suzie Q'},
        {'name': 'Jean Blasin'},
    ],
    'pets': [Pet('Cinnamon')]
}
org_walk = Walk('org')

@mark.parametrize(
    ['walk', 'expected_value'],
    [
        (Walk / 'name', 'Suzie Q'),
        (Walk() / 'name', 'Suzie Q'),
        (Walk('name'), 'Suzie Q'),
        (Walk('org', 'address') / 'country', 'France'),
        (org_walk / 'title', 'Datawalk'),
        (Walk / 'org' / 'phones' / 1, '02 13 46 58 79'),
        (org_walk / (666, 'ev/l'), 'hashable key'),
        (Walk() / 'friends' / 0 / 'name', 'Frankie Manning'),
        (Walk() / 'pets' / 0 / 'name', 'Cinnamon'),
        (Walk() / 'friends' / slice(1, -1), [
            {'name': 'Harry Cover'},
            {'name': 'Suzie Q'}
        ]),
    ]
)
def test_walk_get_value(walk: Walk, expected_value):
    assert walk.walk(data) == expected_value

def test_walk_invalid_path_without_default():
    with raises(Exception) as error:
        (org_walk  / 'phones' / 1 / 'phone').walk(data)
    
    assert str(error.value) == 'walked [.org, .phones, [1]] but could not find .phone in 02 13 46 58 79'

def test_walk_invalid_path_with_default():
    assert (org_walk  / 'phones' / 1 / 'phone').walk(data, default=None) is None
    
