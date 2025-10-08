"""
Eases data retrieval in nested structures by providing a DSL based on the magic methods involved with arithmetic operators
- operators and magic methods: https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types
- operator precedence: https://docs.python.org/3/reference/expressions.html#operator-precedence
"""

from __future__ import annotations

from typing import Any, Hashable, Protocol, Sequence

from datawalk.errors import SelectorError, WalkError
from datawalk.filters.all import All
from datawalk.filters.first import First
from datawalk.selectors.by_key import ByKey
from datawalk.selectors.by_slice import BySlice


class Selector(Protocol):
    def __call__(self, state: Any) -> Any: ...


class MetaWalk(type):
    def __truediv__(cls, step: Hashable) -> Walk:
        return Walk(Walk.build_selector(step))


# flag used when walking a data structure without a default value
_NO_DEFAULT = object()


class Walk(metaclass=MetaWalk):
    def __init__(self, *selectors: Selector):
        """
        Should only be used internally
        """
        self.selectors = tuple(selectors)

    @staticmethod
    def build_selector(step: Hashable | slice) -> Selector:
        if isinstance(step, slice):
            return BySlice(step)
        else:
            return ByKey(step)

    def __truediv__(self, step: Hashable | slice) -> Walk:
        return Walk(*self.selectors, Walk.build_selector(step))

    def __matmul__(self, filter: Sequence[Hashable, Hashable]) -> Any:
        """
        In a sequence, selects the first entry whose key has the given value
        """
        match filter:
            case [key, value]:
                return Walk(*self.selectors, First(key, value))

            case _:
                raise SelectorError(f'unsupported filter: {filter}')

    def __mod__(self, filter: Sequence[Hashable, Sequence]):
        """
        In a sequence, selects the entries whose key has a value in the given sequence
        """
        match filter:
            case [key, [*values]]:
                return Walk(*self.selectors, All(key, values))

            case [key, value]:
                raise SelectorError(f'unsupported filter: {filter}, value {value} must be a sequence')

            case _:
                raise SelectorError(f'unsupported filter: {filter}')

    def walk(self, data: dict, /, *, default: Any = _NO_DEFAULT) -> Any:
        current_state = data
        passed_selectors = []
        for selector in self.selectors:
            try:
                current_state = selector(current_state)
                passed_selectors.append(selector)
            except Exception as error:
                if default is _NO_DEFAULT:
                    raise WalkError(
                        f'walked {passed_selectors} but could not find {selector} in {current_state}',
                        data_state=current_state,
                    ) from error
                else:
                    return default

        return current_state

    def __repr__(self) -> str:
        return ' '.join(f'{selector}' for selector in self.selectors)
