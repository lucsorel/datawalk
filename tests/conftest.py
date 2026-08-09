from dataclasses import dataclass
from typing import NamedTuple

from pytest import fixture


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


@fixture
def pets() -> tuple[Pet, PetDataclass, Pet, PetNamedTuple]:
    return (
        Pet('Cinnamon', 'cat'),
        PetDataclass('Caramel', 'dog'),
        Pet('Melody', 'bird'),
        PetNamedTuple('Socks', 'cat'),
    )


@fixture
def pets_by_name() -> dict[str, Pet | PetDataclass | PetNamedTuple]:
    return {
        'Cinnamon': Pet('Cinnamon', 'cat'),
        'Caramel': PetDataclass('Caramel', 'dog'),
        'Melody': Pet('Melody', 'bird'),
        'Socks': PetNamedTuple('Socks', 'cat'),
    }


@fixture
def friends() -> list[dict]:
    return [
        {'name': 'Frankie Manning'},
        {'name': 'Harry Cover'},
        {'name': 'Suzie Q', 'phone': '06 43 15 27 98'},
        {'name': 'Jean Blasin'},
    ]
