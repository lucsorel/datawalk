from pytest import mark

from datawalk import Walk
from datawalk.selectors.by_key import ByKey

from tests.conftest import Pet, PetDataclass, PetNamedTuple


@mark.parametrize(
    ['key', 'expected_repr'],
    [
        ('name', '.name'),
        (1, '[1]'),
        # a tuple with immutable values can be a dict key
        ((1, 'tuple'), ".(1, 'tuple')"),
    ],
)
def test_bykey_repr(key, expected_repr):
    assert repr(ByKey(key)) == expected_repr


def test_bykey_call_pets(pets: tuple[Pet, PetDataclass, Pet, PetNamedTuple]):
    pet_name_picker = ByKey('name')
    for pet, expected_name in zip(
        pets,
        (
            'Cinnamon',
            'Caramel',
            'Melody',
            'Socks',
        ),
        strict=True,
    ):
        assert pet_name_picker(pet) == expected_name


def test_bykey_call_sequence(friends: list[dict]):
    selector = ByKey(2)
    assert selector(friends) == {'name': 'Suzie Q', 'phone': '06 43 15 27 98'}


def test_walk_repr_with_bykey():
    assert repr(Walk / 2 / 'name') == '[2] .name'


def test_walk_with_bykey_selector(friends: list[dict]):
    assert Walk / 2 / 'name' | friends == 'Suzie Q'
