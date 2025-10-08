from typing import Any, Hashable, Iterable

from datawalk.filters import value_getter


class First:
    def __init__(self, key: Hashable, value: Any):
        self.key = key
        self.value = value

    def __call__(self, state: Iterable[dict | object]) -> Any:
        """
        Raises:
            StopIteration: if the state sequence contains no item with the given key and value
        """
        if len(state) == 0:
            return None

        return next(item for item in state if value_getter(item, self.key) == self.value)

    def __repr__(self) -> str:
        return f'@({self.key}=={self.value})'
