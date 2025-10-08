from typing import Sequence


class BySlice:
    """
    Returns the values corresponding with the given slice.
    """

    def __init__(self, slicer: slice):
        self.slicer = slicer

    def __call__(self, state: Sequence) -> Sequence:
        """
        Apply the specified slice on the given sequence state

        TODO: test with namedtuple
        """
        return state[self.slicer]

    def __repr__(self) -> str:
        indices = [str(index) if index is not None else '' for index in (self.slicer.start, self.slicer.stop)]

        if self.slicer.step is not None:
            indices.append(str(self.slicer.step))

        return f'[{":".join(indices)}]'
