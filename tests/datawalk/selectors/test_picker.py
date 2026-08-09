from pytest import mark

from datawalk import Walk
from datawalk.selectors.picker import Picker

from tests.conftest import Pet, PetDataclass, PetNamedTuple


@mark.parametrize(
    ('picker', 'expected_repr'),
    [
        (Picker(('firstname', 'lastname')), '{firstname,lastname}'),
        (Picker((0, 3)), '{0,3}'),
    ],
)
def test_picker_repr(picker, expected_repr):
    assert repr(picker) == expected_repr


@mark.parametrize(
    ['walk', 'expected_repr'],
    [
        (Walk // ('city', 'zipcode'), '{city,zipcode}'),
        (Walk // ('type',), '{type}'),
        (Walk // (0, 2), '{0,2}'),
    ],
)
def test_walk_repr_with_picker(walk, expected_repr):
    assert repr(walk) == expected_repr


def test_picker_call_dict():
    address = {'country': 'France', 'city': 'Rennes', 'zipcode': '35700'}
    picker = Picker(('city', 'zipcode'))
    assert picker(address) == {'city': 'Rennes', 'zipcode': '35700'}


def test_picker_call_sequence():
    countries = 'France', 'Germany', 'Japan'
    picker = Picker((0, 2))
    assert picker(countries) == {0: 'France', 2: 'Japan'}


def test_picker_call_pets(pets: tuple[Pet, PetDataclass, Pet, PetNamedTuple]):
    pet_type_picker = Picker(('type',))
    for pet, expected_type in zip(
        pets,
        (
            'cat',
            'dog',
            'bird',
            'cat',
        ),
        strict=True,
    ):
        assert pet_type_picker(pet) == {'type': expected_type}


@mark.parametrize(
    ['walk', 'state', 'expected_result'],
    [
        (
            Walk // ('city', 'zipcode'),
            {'country': 'France', 'city': 'Rennes', 'zipcode': '35700'},
            {'city': 'Rennes', 'zipcode': '35700'},
        ),
        (Walk // ('type',), Pet(name='Bémol', type='cat'), {'type': 'cat'}),
        (Walk // (0, 2), ['France', 'Germany', 'Japan'], {0: 'France', 2: 'Japan'}),
        (Walk // (0, 2), ('France', 'Germany', 'Japan'), {0: 'France', 2: 'Japan'}),
    ],
)
def test_walk_with_picker(walk, state, expected_result):
    assert walk | state == expected_result
