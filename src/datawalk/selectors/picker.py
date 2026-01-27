from typing import Hashable, Sequence

from datawalk.selectors.by_key import ByKey


class Picker:
    def __init__(self, pickers: Sequence[Hashable]):
        self.pickers = tuple(ByKey(picker) for picker in pickers)

    def __call__(self, state: dict | object) -> dict:
        return {picker.key: picker(state) for picker in self.pickers}

    def __repr__(self) -> str:
        return f'{{{",".join(str(picker.key) for picker in self.pickers)}}}'
