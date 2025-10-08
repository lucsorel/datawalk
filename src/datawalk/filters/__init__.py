from typing import Hashable

_DEFAULT = object()


def value_getter(item: dict | object, key: Hashable):
    if isinstance(item, dict):
        return item.get(key, _DEFAULT)
    else:
        return getattr(item, key, _DEFAULT)
