from datawalk import Walk

from pytest import mark, raises

class Pet:
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self) -> str:
        return f'Pet(name={self.name})'

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
        {'name': 'Suzie Q', 'phone': '06 43 15 27 98'},
        {'name': 'Jean Blasin'},
    ],
    'pets': [Pet('Cinnamon'), Pet('Caramel')]
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
            {'name': 'Suzie Q', 'phone': '06 43 15 27 98'}
        ]),
    ]
)
def test_walk_get_value(walk: Walk, expected_value):
    assert walk.walk(data) == expected_value

@mark.parametrize(
    ['invalid_walk', 'expected_error_message'],
    [
        (Walk / 'org' / 'phones' / 1 / 'phone', 'walked [.org, .phones, [1]] but could not find .phone in 02 13 46 58 79'),
        (Walk / 'pets' % ('name', 'Vanilla') / 'name', 'walked [.pets] but could not find .name==Vanilla in [Pet(name=Cinnamon), Pet(name=Caramel)]'),
    ],
)
def test_walk_invalid_path_without_default(invalid_walk, expected_error_message):
    with raises(Exception) as error:
        invalid_walk.walk(data)

    assert str(error.value) == expected_error_message

@mark.parametrize(
    ['invalid_walk'],
    [
        (Walk / 'org' / 'phones' / 1 / 'phone',),
        (Walk / 'friends' % ('name', 'John Doe'),),
        (Walk / 'pets' % ('name', 'Vanilla') / 'name',),
    ],
)
def test_walk_invalid_path_with_default(invalid_walk: Walk):
    assert invalid_walk.walk(data, default=None) is None

@mark.parametrize(
    ['walk', 'expected_value'],
    [
        (Walk / 'friends' % ('name', 'Suzie Q') / 'phone', '06 43 15 27 98'),
        (Walk/ 'pets' % ('name', 'Caramel') / 'name', 'Caramel'),
    ],
)
def test_walk_with_selector(walk, expected_value):
    assert walk.walk(data) == expected_value
