"""
Eases data retrieval in nested structures by providing a DSL based on the magic methods involved with arithmetic operators
- operators and special methods: https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types
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
    """
    Allows to create a Walk instance by applying the selector operators directly on the Walk class
    >>> Walk / 'key'
    >>> Walk @ ('key', value)
    >>> Walk % ('key', value)
    """

    def __truediv__(cls, step: Hashable) -> Walk:
        return Walk(Walk.build_selector(step))

    def __matmul__(cls, filter: Sequence[Hashable, Hashable]) -> Any:
        return Walk() @ filter

    def __mod__(cls, filter: Sequence[Hashable, Sequence]):
        return Walk() % filter


class Walk(metaclass=MetaWalk):
    """
    A walk is an immutable sequence of selectors that can be applied on a dataset to return the corresponding value.
    The immutability ensures that the walk:
    - can be applied on different datasets
    - can be combined with other walks without being modified, by produce a new deeper walk

    There are 2 groups of selector operators:
    - the ones that return a selected value: `/ 'key'` and `@ ('key', value)`
    - the ones that return a sequence of values: `/ slice(...)` and `% ('key', value)`
    """

    # flag used when walking a data structure without a default value
    _NO_DEFAULT = object()

    def __init__(self, *selectors: Selector):
        """
        Used internally to create a new walk combining the selectors of different walks.
        """
        self.selectors = tuple(selectors)

    @staticmethod
    def build_selector(step: Hashable | slice) -> Selector:
        if isinstance(step, slice):
            return BySlice(step)
        else:
            return ByKey(step)

    def __truediv__(self, step: Hashable | slice) -> Walk:
        """
        Creates a new walk combining the current selectors with the one corresponding to the given step.
        >>> walk / 'name'         # dict key or argument name
        >>> walk / 0              # sequence index
        >>> walk / slice(1,-1, 2) # applies the [1, -1, 2] slice on the sequence

        Special case: passing an ellipsis returns a walk without the last selector
        >>> walk / 'key' / ...    # returns a walk without the 'key' selector
        """
        if step is Ellipsis:
            return Walk(*self.selectors[:-1])
        else:
            return Walk(*self.selectors, Walk.build_selector(step))

    def __matmul__(self, filter: Sequence[Hashable, Hashable]) -> Any:
        """
        In a sequence, selects the first entry whose key has the given value
        >>> walk @ (key, value)
        """

        match filter:
            case [key, value]:
                return Walk(*self.selectors, First(key, value))

            case _:
                raise SelectorError(f'unsupported filter: {filter}')

    def __mod__(self, filter: Sequence[Hashable, Sequence]):
        """
        In a sequence, selects the entries whose key has a value in the given sequence
        >>> walk % (key, value)
        """

        match filter:
            case [key, [*values]]:
                return Walk(*self.selectors, All(key, values))

            case [key, value]:
                raise SelectorError(f'unsupported filter: {filter}, value {value} must be a sequence')

            case _:
                raise SelectorError(f'unsupported filter: {filter}')

    def __add__(self, other_walk) -> Walk:
        """
        Enables the use of the "+" add operator to produce a new walk combining the selectors of the current walk with
        the ones of the other walk.
        >>> walk + other_walk # produces a new walk
        """
        if isinstance(other_walk, Walk):
            return Walk(*self.selectors, *other_walk.selectors)

        return NotImplemented

    def __or__(self, data: dict | object) -> Any:
        """
        Enables the use of the "|" or operator to apply the walk's selectors on the given dataset
        >>> walk | data

        Raises:
            WalkError: when one of the selectors fails to return a value
        """
        return self.walk(data)

    def __xor__(self, data_with_default_value: Sequence[dict | object, Any]) -> Any:
        """
        Enables the use of the "^" xor operator to apply the walk's selectors on the given dataset
        with a default value if a selector fails to return a value
        >>> walk ^ (data, default_value)

        Raises:
            TypeError: if the given value is not an iterable that can be unpacked
            ValueError: if the given iterable could not be unpacked into 2 values
        """

        data, default_value = data_with_default_value
        return self.walk(data, default=default_value)

    def walk(self, data: dict | object, /, *, default: Any = _NO_DEFAULT) -> Any:
        """
        Applies the walk's selectors on the given dataset and returns the final result
        """
        current_state = data
        passed_selectors = []
        for selector in self.selectors:
            try:
                current_state = selector(current_state)
                passed_selectors.append(selector)
            except Exception as error:
                if default is Walk._NO_DEFAULT:
                    raise WalkError(
                        f'walked {passed_selectors} but could not find {selector} in {current_state}',
                        data_state=current_state,
                    ) from error
                else:
                    return default

        return current_state

    def __repr__(self) -> str:
        return ' '.join(f'{selector}' for selector in self.selectors)
