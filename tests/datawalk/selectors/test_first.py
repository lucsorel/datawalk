from datawalk import Walk
from datawalk.selectors.first import First

from tests.conftest import Pet, PetDataclass, PetNamedTuple


def test_first_repr():
    assert repr(First('type', 'dog')) == '@(type==dog)'


def test_first_call_pets(pets: tuple[Pet, PetDataclass, Pet, PetNamedTuple]):
    selector = First('type', 'dog')
    _, caramel, _, _ = pets
    assert selector(pets) == caramel


def test_first_call_on_empty_sequence():
    selector = First('type', 'dog')
    assert selector([]) is None


def test_walk_with_first_selector(pets: tuple[Pet, PetDataclass, Pet, PetNamedTuple]):
    _, caramel, _, _ = pets
    assert Walk @ ('type', 'dog') | pets == caramel
