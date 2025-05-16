from __future__ import annotations

from typing import Any, Hashable, Sequence


class Step:
    def __init__(self, key: Hashable):
        self.key = key

    def __call__(self, state: dict | Sequence | object):
        if isinstance(state, (dict, Sequence)):
            return state[self.key]
        else:
            return getattr(state, self.key)

    def __repr__(self):
        return f"Step({self.key})"

class MetaWalk(type):
    def __truediv__(self, key: Hashable) -> Walk:
        return Walk(key)

_NO_DEFAULT = ()
class Walk(metaclass=MetaWalk):
    def __init__(self, *keys: Hashable):
        self.steps = tuple(Step(key) for key in keys)

    @staticmethod
    def from_steps(*steps: Step):
        walk = Walk()
        walk.steps = steps
        return walk

    def __truediv__(self: Walk, key: Hashable|slice) -> Walk:
        return Walk.from_steps(*self.steps, Step(key))

    def walk(self, data: dict, /,*, default: Any = _NO_DEFAULT) -> Any:
        current_state = data
        passed_steps = []
        for step in self.steps:
            try:
                current_state = step(current_state)
                passed_steps.append(step)
            except Exception as error:
                if default is _NO_DEFAULT:
                    raise Exception(f"could not find {step} at {passed_steps} in {current_state}") from error
                else:
                    return default 

        return current_state

if __name__ == "__main__":
    walk_from_class = Walk / 'property'
    walk_from_instance = Walk('property_1', 'property_2') / 'property_3'
    select_friends = Walk / 'property' / slice(0, -1)
    print(f"{walk_from_class.steps=}")
    print(f"{walk_from_instance.steps=}")
    print(f"{select_friends.steps=}")
