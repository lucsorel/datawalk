from typing import Any

from pytest import fixture, mark, raises

from datawalk import Walk
from datawalk.errors import SelectorError, WalkError

from tests.conftest import Pet, PetDataclass, PetNamedTuple


@fixture
def data(pets) -> dict:
    return {
        'name': 'Lucie Nation',
        'org': {
            'title': 'Datawalk',
            'address': {'country': 'France', 'city': 'Rennes', 'zipcode': '35700'},
            'phones': ['01 23 45 67 89', '02 13 46 58 79'],
            (666, 'ev/l'): 'hashable key',
        },
        'friends': [
            {'name': 'Frankie Manning'},
            {'name': 'Harry Cover'},
            {'name': 'Suzie Q', 'phone': '06 43 15 27 98'},
            {'name': 'Jean Blasin'},
        ],
        'pets': pets,
    }


def test_walks_are_immutable_when_appending_selectors():
    org_walk = Walk / 'org'
    org_walk_repr = repr(org_walk)
    assert org_walk_repr == '.org'

    org_country_walk = org_walk / 'address' / 'country'
    assert repr(org_country_walk) == '.org .address .country'
    assert repr(org_walk) == org_walk_repr, 'applying new selectors does not modify the walk, it creates a new one'


def test_walks_are_immutable_when_combining_walks():
    org_walk = Walk / 'org'
    org_walk_repr = repr(org_walk)
    assert org_walk_repr == '.org'

    country_walk = Walk / 'address' / 'country'
    country_walk_repr = repr(country_walk)
    assert country_walk_repr == '.address .country'

    org_country_walk = org_walk + country_walk
    assert repr(org_country_walk) == '.org .address .country'
    assert repr(org_walk) == org_walk_repr, 'combining 2 walks does not modify the 1st walk, it creates a new one'
    assert repr(country_walk) == country_walk_repr, (
        'combining 2 walks does not modify the 2nd walk, it creates a new one'
    )


@mark.parametrize(
    ['walk', 'expected_value'],
    [
        (Walk() / 'name', 'Lucie Nation'),
        (Walk / 'name', 'Lucie Nation'),
        (Walk / 'org' / 'address' / 'country', 'France'),
        (Walk / 'org' / 'address' // ('city', 'zipcode'), {'city': 'Rennes', 'zipcode': '35700'}),
        (Walk / 'org' / 'title', 'Datawalk'),
        (Walk / 'org' / 'phones' / 1, '02 13 46 58 79'),
        (Walk / 'org' / (666, 'ev/l'), 'hashable key'),
        (Walk / 'friends' / 0 / 'name', 'Frankie Manning'),
        (Walk / 'friends' // (0, 3), {0: {'name': 'Frankie Manning'}, 3: {'name': 'Jean Blasin'}}),
        (Walk / 'pets' / 0 / 'name', 'Cinnamon'),
        (
            Walk / 'friends' / slice(1, -1),
            [{'name': 'Harry Cover'}, {'name': 'Suzie Q', 'phone': '06 43 15 27 98'}],
        ),
    ],
)
def test_walk_get_value(data: dict, walk: Walk, expected_value):
    assert walk.walk(data) == expected_value


def test_walk_with_ellipsis(data: dict):
    suzie_name_walk = Walk / 'friends' @ ('name', 'Suzie Q') / 'name'
    suzie_name_walk_repr = repr(suzie_name_walk)
    assert suzie_name_walk_repr == '.friends @(name==Suzie Q) .name'
    assert suzie_name_walk | data == 'Suzie Q'

    suzie_phone_walk = suzie_name_walk / ... / 'phone'
    assert repr(suzie_phone_walk) == '.friends @(name==Suzie Q) .phone'
    assert suzie_phone_walk | data == '06 43 15 27 98'

    assert repr(suzie_name_walk) == suzie_name_walk_repr, (
        'using an ellipsis does not modify a walk, it creates a new walk'
    )


def test_walk_invalid_selector():
    with raises(SelectorError) as error:
        Walk / 'pets' % ('type', 'cat')

    assert str(error.value) == "unsupported filter: ('type', 'cat'), value cat must be a sequence"


@mark.parametrize(
    ['invalid_walk', 'expected_error_message', 'current_data_state'],
    [
        (
            Walk / 'org' / 'phones' / 1 / 'phone',
            'walked [.org, .phones, [1]] but could not find .phone in the current data state',
            '02 13 46 58 79',
        ),
        (
            Walk / 'friends' @ ('name', 'Suzie Q') / 'phone_number',
            'walked [.friends, @(name==Suzie Q)] but could not find .phone_number in the current data state',
            {'name': 'Suzie Q', 'phone': '06 43 15 27 98'},
        ),
        (
            Walk / 'pets' @ ('name', 'Vanilla') / 'name',
            'walked [.pets] but could not find @(name==Vanilla) in the current data state',
            (
                Pet(name='Cinnamon', type='cat'),
                PetDataclass(name='Caramel', type='dog'),
                Pet(name='Melody', type='bird'),
                PetNamedTuple(name='Socks', type='cat'),
            ),
        ),
    ],
)
def test_walk_invalid_path_without_default(
    data: dict, invalid_walk: Walk, expected_error_message: str, current_data_state
):
    with raises(WalkError) as error:
        invalid_walk.walk(data)

    walk_error: WalkError = error.value
    assert str(walk_error) == expected_error_message
    assert walk_error.data_state == current_data_state


@mark.parametrize(
    ['invalid_walk'],
    [
        (Walk / 'org' / 'phones' / 1 / 'phone',),
        (Walk / 'friends' @ ('name', 'John Doe'),),
        (Walk / 'pets' @ ('name', 'Vanilla') / 'name',),
    ],
)
def test_walk_invalid_path_with_default(data: dict, invalid_walk: Walk):
    assert invalid_walk.walk(data, default=None) is None


@mark.parametrize(
    ['walk', 'expected_value'],
    [
        (Walk / 'friends' @ ('name', 'Suzie Q') / 'phone', '06 43 15 27 98'),
        (Walk / 'pets' @ ('name', 'Caramel') / 'name', 'Caramel'),
        (Walk / 'pets' @ ('name', 'Cinnamon') / 'type', 'cat'),
        (Walk / 'pets' % ('type', ['cat']) / 0 / 'name', 'Cinnamon'),
        (Walk / 'pets' % ('type', ['cat']) / 1 / 'name', 'Socks'),
        (Walk / 'pets' % ('type', ['dog']) / 0 / 'name', 'Caramel'),
    ],
)
def test_walk_with_filter(data: dict, walk: Walk, expected_value: Any):
    assert walk.walk(data) == expected_value


def test_walk_with_invalid_filter_first():
    with raises(SelectorError) as selector_error:
        Walk @ ('key_without_value')

    assert str(selector_error.value) == 'unsupported filter: key_without_value'


def test_walk_with_invalid_filter_all():
    with raises(SelectorError) as selector_error:
        Walk % ('key_without_values')

    assert str(selector_error.value) == 'unsupported filter: key_without_values'


def test_walk_with_invalid_concatenation():
    with raises(TypeError) as type_error:
        (Walk / 'friends' / 0) + 'name'

    assert str(type_error.value) == "unsupported operand type(s) for +: 'Walk' and 'str'"


@mark.parametrize(
    ['walk', 'expected_repr'],
    [
        (Walk / 'org' / 'address' // ('city', 'zipcode'), '.org .address {city,zipcode}'),
        (Walk / 'pets' % ('name', ['Melody', 'Socks']), ".pets %(name in ['Melody', 'Socks'])"),
    ],
)
def test_walk_repr(walk, expected_repr):
    assert repr(walk) == expected_repr


def test_walk_with_operators(data: dict, pets):
    assert Walk / 'pets' @ ('name', 'Cinnamon') / 'name' | data == 'Cinnamon'
    assert Walk / 'pets' @ ('name', 'Cinnamon') + Walk / 'name' | data == 'Cinnamon'
    assert Walk / 'pets' @ ('name', 'Raspberry') / 'name' ^ (data, '☹️ no Raspberry') == '☹️ no Raspberry'
    # walks on list
    assert Walk @ ('name', 'Cinnamon') + Walk / 'name' | pets == 'Cinnamon'
    assert Walk % ('type', ['dog']) / 0 / 'name' | pets == 'Caramel'
    # pick key:value items
    assert Walk // ('name', 'pets') | data == {'name': 'Lucie Nation', 'pets': pets}
