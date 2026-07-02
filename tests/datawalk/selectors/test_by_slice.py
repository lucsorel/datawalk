from pytest import mark

from datawalk import Walk
from datawalk.selectors.by_slice import BySlice

from tests.conftest import Pet, PetDataclass, PetNamedTuple


@mark.parametrize(
    ['slice_value', 'expected_repr'],
    [
        (slice(3), '[:3]'),
        (slice(2, 4), '[2:4]'),
        (slice(3, 1, -1), '[3:1:-1]'),
        (slice(1, None), '[1:]'),
        (slice(None, 3), '[:3]'),
        (slice(3, None, -1), '[3::-1]'),
        (slice(None, 3, -1), '[:3:-1]'),
    ],
)
def test_byslice_repr(slice_value, expected_repr):
    assert repr(BySlice(slice_value)) == expected_repr


@mark.parametrize(
    ['slice_value', 'expected_pets_by_names'],
    [
        (slice(1), ['Cinnamon']),
        (slice(2, 4), ['Melody', 'Socks']),
        (slice(3, 1, -1), ['Socks', 'Melody']),
        (slice(2, None), ['Melody', 'Socks']),
        (slice(None, 2), ['Cinnamon', 'Caramel']),
        (slice(2, None, -1), ['Melody', 'Caramel', 'Cinnamon']),
        (slice(None, 1, -1), ['Socks', 'Melody']),
    ],
)
def test_byslice_call_pets(
    pets_by_name: dict[str, Pet | PetDataclass | PetNamedTuple], slice_value, expected_pets_by_names
):
    # pets are Cinnamon, Caramel, Melody, Socks
    pets_selector = BySlice(slice_value)
    assert pets_selector(list(pets_by_name.values())) == [pets_by_name[pet_name] for pet_name in expected_pets_by_names]


def test_byslice_call_sequence(friends: list[dict]):
    selector = BySlice(2)
    assert selector(friends) == {'name': 'Suzie Q', 'phone': '06 43 15 27 98'}


def test_walk_repr_with_byslice():
    assert repr(Walk / 2 / 'name') == '[2] .name'


def test_walk_with_byslice_selector(friends: list[dict]):
    assert Walk / 2 / 'name' | friends == 'Suzie Q'
