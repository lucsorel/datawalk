"""
Eases data retrieval in nested structures by providing a DSL based on the magic methods involved with arithmetic operators
- operators and magic methods: https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types
- operator precedence: https://docs.python.org/3/reference/expressions.html#operator-precedence
"""

from __future__ import annotations

from typing import Any, Hashable, Sequence


class Step:
    """
    Returns the value associated with the given key:
    - an index or a slice (start, stop, step) for a sequence
    - a key for a dict
    - an attribute name otherwise
    """

    def __init__(self, key: Hashable):
        self.key = key

    def __call__(self, state: dict | Sequence | object):
        if isinstance(state, (dict, Sequence)):
            return state[self.key]
        else:
            return getattr(state, self.key)

    def __repr__(self) -> str:
        if isinstance(self.key, slice):
            indices = [
                str(index) if index is not None else ''
                for index in (self.key.start, self.key.stop)
            ]
            if self.key.step is not None:
                indices.append(str(self.key.step))
            return f"[{':'.join(indices)}]"
        elif isinstance(self.key, int):
            return f'[{self.key}]'
        else:
            return f'.{self.key}'

class OneItemSelector:
    """
    Selects the first item in a sequence whose given property equals the given value
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __call__(self, state: Sequence):
        if len(state) == 0:
            return None

        value_getter = self.dict_value_getter if isinstance(state[0], dict) else self.object_value_getter

        return next(item for item in state if value_getter(item, self.key) == self.value)

    def __repr__(self) -> str:
        return f'.{self.key}=={self.value}'

    @staticmethod
    def dict_value_getter(state: dict, key: Any):
        return state.get(key)

    @staticmethod
    def object_value_getter(state: object, key: Any):
        return getattr(state, key, None)

class MetaWalk(type):
    def __truediv__(self, key: Hashable) -> Walk:
        return Walk(key)

_NO_DEFAULT = ()
class Walk(metaclass=MetaWalk):
    def __init__(self, *keys: Hashable):
        self.steps = tuple(Step(key) for key in keys)

    @staticmethod
    def from_steps(*steps: Step | OneItemSelector):
        walk = Walk()
        walk.steps = steps
        return walk

    def __truediv__(self, key: Hashable | slice) -> Walk:
        return Walk.from_steps(*self.steps, Step(key))

    def __mod__(self, filter):
        match filter:
            case key, value:
                return Walk.from_steps(*self.steps, OneItemSelector(key, value))

            case _:
                raise ValueError(f'unsupported filter: {filter}')

    def walk(self, data: dict, /,*, default: Any = _NO_DEFAULT) -> Any:
        current_state = data
        passed_steps = []
        for step in self.steps:
            try:
                current_state = step(current_state)
                passed_steps.append(step)
            except Exception as error:
                if default is _NO_DEFAULT:
                    raise Exception(f'walked {passed_steps} but could not find {step} in {current_state}') from error
                else:
                    return default 

        return current_state

if __name__ == '__main__':
    walk_from_class = Walk / 'property'
    walk_from_instance = Walk('property_1', 'property_2') / 'property_3'
    select_items = Walk / 'property' / slice(0, -1)
    filter_item = Walk / 'property' % ('key', 'value')
    print(f'{walk_from_class.steps=}')
    print(f'{walk_from_instance.steps=}')
    print(f'{select_items.steps=}')
    print(f'{filter_item.steps=}')
