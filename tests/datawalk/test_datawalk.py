from dataclasses import dataclass
from typing import Any, NamedTuple

from pytest import fixture, mark, raises

from datawalk import Walk
from datawalk.errors import SelectorError, WalkError


class Pet:
    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type

    def __repr__(self) -> str:
        return f'Pet(name={self.name}, type={self.type})'

    def __eq__(self, other) -> str:
        return other is not None and isinstance(other, Pet) and other.name == self.name and other.type == self.type


@dataclass
class PetDataclass:
    name: str
    type: str


class PetNamedTuple(NamedTuple):
    name: str
    type: str


def pets():
    return (
        Pet('Cinnamon', 'cat'),
        PetDataclass('Caramel', 'dog'),
        Pet('Melody', 'bird'),
        PetNamedTuple('Socks', 'cat'),
    )


@fixture(scope='session')
def data() -> dict:
    return {
        'name': 'Lucie Nation',
        'org': {
            'title': 'Datawalk',
            'address': {'country': 'France'},
            'phones': ['01 23 45 67 89', '02 13 46 58 79'],
            (666, 'ev/l'): 'hashable key',
        },
        'friends': [
            {'name': 'Frankie Manning'},
            {'name': 'Harry Cover'},
            {'name': 'Suzie Q', 'phone': '06 43 15 27 98'},
            {'name': 'Jean Blasin'},
        ],
        'pets': pets(),
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
        (Walk / 'org' / 'title', 'Datawalk'),
        (Walk / 'org' / 'phones' / 1, '02 13 46 58 79'),
        (Walk / 'org' / (666, 'ev/l'), 'hashable key'),
        (Walk / 'friends' / 0 / 'name', 'Frankie Manning'),
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
    ['invalid_walk', 'expected_error_message'],
    [
        (
            Walk / 'org' / 'phones' / 1 / 'phone',
            'walked [.org, .phones, [1]] but could not find .phone in 02 13 46 58 79',
        ),
        (
            Walk / 'friends' @ ('name', 'Suzie Q') / 'phone_number',
            "walked [.friends, @(name==Suzie Q)] but could not find .phone_number in {'name': 'Suzie Q', 'phone': '06 43 15 27 98'}",
        ),
        (
            Walk / 'pets' @ ('name', 'Vanilla') / 'name',
            "walked [.pets] but could not find @(name==Vanilla) in (Pet(name=Cinnamon, type=cat), PetDataclass(name='Caramel', type='dog'), Pet(name=Melody, type=bird), PetNamedTuple(name='Socks', type='cat'))",
        ),
    ],
)
def test_walk_invalid_path_without_default(data: dict, invalid_walk: Walk, expected_error_message: str):
    with raises(WalkError) as error:
        invalid_walk.walk(data)

    assert str(error.value) == expected_error_message


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


cinnamon, caramel, melody, socks = pets()


@mark.parametrize(
    ['walk', 'expected_value'],
    [
        (Walk / 'friends' @ ('name', 'Suzie Q') / 'phone', '06 43 15 27 98'),
        (Walk / 'pets' @ ('name', 'Caramel') / 'name', 'Caramel'),
        (Walk / 'pets' @ ('name', 'Cinnamon'), cinnamon),
        (Walk / 'pets' % ('name', ['Cinnamon', 'Melody']), [cinnamon, melody]),
        (Walk / 'pets' % ('type', ['cat']), [cinnamon, socks]),
        (Walk / 'pets' % ('type', ['cat']) / 1 / 'name', 'Socks'),
        (Walk / 'pets' % ('type', ['dog']), [caramel]),
    ],
)
def test_walk_with_filter(data: dict, walk: Walk, expected_value: Any):
    assert walk.walk(data) == expected_value


def test_walk_with_operators(data: dict):
    assert Walk / 'pets' @ ('name', 'Cinnamon') / 'name' | data == 'Cinnamon'
    assert Walk / 'pets' @ ('name', 'Cinnamon') + Walk / 'name' | data == 'Cinnamon'
    assert Walk / 'pets' @ ('name', 'Raspberry') / 'name' ^ (data, '☹️ no Raspberry') == '☹️ no Raspberry'
    # walks on list
    assert Walk @ ('name', 'Cinnamon') + Walk / 'name' | data['pets'] == 'Cinnamon'
    assert Walk % ('type', ['dog']) / 0 / 'name' | data['pets'] == 'Caramel'
