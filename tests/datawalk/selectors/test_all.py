from datawalk import Walk
from datawalk.selectors.all import All

from tests.conftest import Pet, PetDataclass, PetNamedTuple


def test_all_repr():
    assert repr(All('type', ['cat', 'dog'])) == "%(type in ['cat', 'dog'])"


def test_all_call_pets(pets: tuple[Pet, PetDataclass, Pet, PetNamedTuple]):
    selector = All('type', ['cat', 'dog'])
    cinnamon, caramel, _, socks = pets
    assert selector(pets) == [cinnamon, caramel, socks]


def test_all_call_on_empty_sequence():
    selector = All('type', ['cat', 'dog'])
    assert selector([]) == []


def test_walk_with_all_selector(pets: tuple[Pet, PetDataclass, Pet, PetNamedTuple]):
    cinnamon, caramel, _, socks = pets
    assert Walk % ('type', ['cat', 'dog']) | pets == [cinnamon, caramel, socks]
