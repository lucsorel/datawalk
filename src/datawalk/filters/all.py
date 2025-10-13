from typing import Hashable, Iterable, Sequence

from datawalk.filters import value_getter


class All:
    def __init__(self, key: Hashable, values: Sequence):
        self.key = key
        self.values = values

    def __call__(self, state: Iterable[dict | object]) -> Sequence:
        """
        Raises:
            StopIteration: if the state sequence contains no item with the given key and value
        """
        if len(state) == 0:
            return []

        return [item for item in state if value_getter(item, self.key) in self.values]

    def __repr__(self) -> str:
        return f'%({self.key} in {self.values})'
