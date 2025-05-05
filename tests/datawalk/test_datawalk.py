from datawalk import DataWalk


def test_data_walk_get_value():
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
            {'name': 'Frankie Manning'}
        ],
        'pets': [Pet('Cinnamon')]
    }
    assert (DataWalk(data) / 'name').get_value() == 'Suzie Q'
    assert (DataWalk(data) / 'org' / 'title').get_value() == 'Datawalk'
    assert (DataWalk(data) / 'org' / 'address' / 'country').get_value() == 'France'
    assert (DataWalk(data) / 'org' / 'phone').get_value() is None
    assert (DataWalk(data) / 'org' / 'phones' / 1).get_value() == '02 13 46 58 79'
    assert (DataWalk(data) / 'org' / (666, 'ev/l')).get_value() == 'hashable key'
    assert (DataWalk(data) / 'friends' / 0 / 'name').get_value() == 'Frankie Manning'
    assert (DataWalk(data) / 'pets' / 0 / 'name').get_value() == 'Cinnamon'
