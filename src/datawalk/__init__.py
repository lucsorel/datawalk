from __future__ import annotations
from typing import Any,Self, Hashable, Sequence

class Key:
    def __init__(self, key: Hashable):
        self.key = key

    def __call__(self, state: dict | list | object):
        if isinstance(state, dict):
            return state.get(self.key)
        elif isinstance(state, Sequence):
            return state[self.key]
        else:
            return getattr(state, self.key)

class DataWalk:
    def __init__(self, data: dict):
        self._data = data
        self._path = []

    def __truediv__(self, key: Hashable) -> Self:
        """
        Handles key after key dict exploration
        https://docs.python.org/3/reference/datamodel.html#object.__truediv__

        TODO: make class immutable
        """
        self._path.append(Key(key))
        return self
    

    def get_value(self, *, default: Any = None) -> Any | None:
        """
        Walks the path and return the value.
        TODO support:
        - trace: bool -> associate the walk to each returned values (when handling filtering list or properties)
        - raise_if_lost: bool -> raise an error () when failing to follow the data path
        """
        current_state = self._data
        for step in self._path:
            try:
                current_state = step(current_state)
            except Exception:
                return default
        
        return current_state
