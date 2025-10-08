class WalkError(LookupError):
    """
    Raised when an error occurred while walking the dataset.
    """

    def __init__(self, /, message, *, data_state=None):
        super().__init__(message)
        self.data_state = data_state


class SelectorError(ValueError):
    """
    Raise when attempting to create an invalid selector or filter
    """

    pass
