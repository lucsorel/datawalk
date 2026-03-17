from pytest import mark

from datawalk import Walk


class FlattenAddress:
    def __call__(self, state: dict) -> dict:
        return {
            'street': state['street'],
            'city': state['city']['name'],
            'zipcode': state['city']['zipcode'],
            'country': state['country']['name'],
        }

    def __repr__(self) -> str:
        return '*address'


ADDRESS = {
    'street': '5 street of Harlem',
    'country': {
        'name': 'United States of America',
        'language': 'en-us',
    },
    'city': {
        'name': 'New York',
        'zipcode': '123456',
    },
}
CONTACT = {'name': 'Suzie Q', 'home_address': ADDRESS}
FLATTENED_ADDRESS = {
    'street': '5 street of Harlem',
    'city': 'New York',
    'zipcode': '123456',
    'country': 'United States of America',
}


@mark.parametrize(
    ['walk', 'expected_representation'],
    [
        (Walk * FlattenAddress(), '*address'),
        (Walk / 'home_address' * FlattenAddress(), '.home_address *address'),
    ],
)
def test_walk_repr_with_custom_selector(walk, expected_representation):
    assert repr(walk) == expected_representation


@mark.parametrize(
    ['walk', 'dataset', 'expected_result'],
    [
        (Walk * FlattenAddress(), ADDRESS, FLATTENED_ADDRESS),
        (Walk / 'home_address' * FlattenAddress(), CONTACT, FLATTENED_ADDRESS),
    ],
)
def test_walk_with_custom_selector(walk, dataset, expected_result):
    assert walk | dataset == expected_result
