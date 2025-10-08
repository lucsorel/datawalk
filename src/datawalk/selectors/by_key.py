from typing import Any, Hashable, Sequence


class ByKey:
    """
    Returns the value associated with the given key:
    - an index for a sequence
    - a key for a dict
    - an attribute name otherwise
    """

    def __init__(self, key: Hashable):
        self.key = key

    def __call__(self, state: dict | Sequence | object) -> Any:
        """
        Retrieves the value associated with the expected key in the given state.

        TODO: test with namedtuple

        Raises:
            AttributeError: when the state object has no attribute with the given name (self.key)
            KeyError: (LookupError) when the state dict does not have the given key (self.key)
            IndexError: (LookupError) when the state dict does not have the given key (self.key)
        """
        if isinstance(state, (dict, Sequence)):
            return state[self.key]
        else:
            return getattr(state, self.key)

    def __repr__(self) -> str:
        if isinstance(self.key, int):
            return f'[{self.key}]'
        else:
            return f'.{self.key}'
