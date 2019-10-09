# -*- coding: utf-8 -*-
"""Contains model classes used by as base for ``newstore.base.Model``
 as well as `newstore.config.NewStoreConfig`.

"""

from thick_denim.ui import UserFriendlyObject

from thick_denim.util import traverse_dict_children


class DataBag(UserFriendlyObject):
    """base-class for config containers"""

    def __init__(self, data: dict = None, *args, **kw):
        data = data or {}
        if not isinstance(data, dict):
            raise TypeError(
                f"{self.__class__.__name__}() requires a dict object, "
                f"but instead got '{data} {type(data)}'."
            )

        self.__data__ = data

    @property
    def data(self):
        return self.__data__

    def update(self, other: dict):
        self.data.update(other or {})

    def traverse(self, *keys, fallback=None):
        """attempts to retrieve the config value under the given nested keys
        """
        value = traverse_dict_children(self.data, *keys, fallback=fallback)
        if isinstance(value, dict):
            return DataSection(value, *keys)

        return value

    def __ui_attributes__(self):
        """converts self.__data__ to dict to prevent recursion error
        """
        return dict(self.__data__)

    # very basic dict compatibility:

    def __iter__(self):
        return iter(self.__data__)

    def __getitem__(self, item):
        return self.__data__[item]

    def __setitem__(self, item, value):
        self.__data__[item] = value

    def keys(self):
        return self.__data__.keys()

    def items(self):
        return self.data.items()

    def values(self):
        return self.data.values()

    def get(self, *args, **kw):
        return self.data.get(*args, **kw)

    # other handy methods:

    def getbool(self, *args, **kw):
        """same as .get() but parses the string value into boolean: `yes` or `true`"""
        value = self.get(*args, **kw)
        if not isinstance(value, str):
            return bool(value)

        value = value.lower().strip()
        return value in ("yes", "true")


class DataSection(DataBag):
    def __init__(self, data, *location):
        self.location = location
        self.attr = ".".join(location)
        super().__init__(data)

    def __ui_attributes__(self):
        """converts self.__data__ to dict to prevent recursion error
        """
        return dict(self.__data__)

    def __ui_name__(self):
        return f"DataSection {self.attr!r} of "
