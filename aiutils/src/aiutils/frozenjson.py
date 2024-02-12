from collections.abc import Mapping, MutableSequence
import keyword
from copy import deepcopy


class FrozenJSON(object):
    """
    A facade for navigating a JSON-like object using attribute notation.
    Based on FrozenJSON from 'Fluent Python'
    """

    def __new__(cls, arg):
        if isinstance(arg, Mapping):
            return super(FrozenJSON, cls).__new__(cls)

        elif isinstance(arg, MutableSequence):
            return [cls(item) for item in arg]
        else:
            return arg

    def __init__(self, mapping):
        self._path_to_file = None

        self._data = {}

        for key, value in mapping.items():
            if keyword.iskeyword(key):
                key += "_"

            self._data[key] = value

    def __getattr__(self, name):
        if hasattr(self._data, name):
            return getattr(self._data, name)
        else:
            return FrozenJSON(self._data[name])

    def __dir__(self):
        return self._data.keys()

    def __getitem__(self, key):
        value = self._data.get(key)

        if value is None:
            key_ = key if not isinstance(key, str) else "'%s'" % key
            msg = "Key error: {}, available keys are: {}".format(
                key_, self._data.keys()
            )
            if self._path_to_file is not None:
                msg += ". File loaded from {}".format(self._path_to_file)
            raise KeyError(msg)

        return value

    def __str__(self):
        if self._path_to_file:
            return self._path_to_file
        else:
            return str(self._data)

    def __repr__(self):
        return "FrozenJSON({})".format(str(self))

    def to_dict(self):
        return deepcopy(self._data)
