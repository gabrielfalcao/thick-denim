# -*- coding: utf-8 -*-
"""
UI-related functions and classes to leverage user-friendly terminal interface
"""
import json


def pretty_json(data, indent=2):
    """serializes the given data into JSON with indentation"""
    return json.dumps(data, indent=2, default=str)


def repr_attributes(attributes: dict, separator: str = " "):
    """used for pretty-printing the attributes of a model
    :param attributes: a dict

    :returns: a string
    """
    return separator.join([f"{k}={v!r}" for k, v in attributes.items()])


def object_is_user_friendly(obj: object) -> bool:
    """check if the given object is user-friendly to be printed on the UI"""
    if isinstance(obj, UserFriendlyObject):
        return True

    if isinstance(obj, (list, tuple, set, bool, str, bytes, int)):
        return True

    return False


class UserFriendlyObject(object):
    def __ui_attributes__(self):
        return dict(
            [
                (key, value)
                for key, value in self.__dict__.items()
                if object_is_user_friendly(value)
            ]
        )

    def __ui_name__(self):
        return self.__class__.__name__

    def __repr__(self):
        attributes = repr_attributes(self.__ui_attributes__())
        return f"<{self.__ui_name__()} {attributes}>"

    def __str__(self):
        attributes = repr_attributes(self.__ui_attributes__(), ", ")
        return f"{self.__ui_name__()}({attributes})"
