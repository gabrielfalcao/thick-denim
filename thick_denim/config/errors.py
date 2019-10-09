# -*- coding: utf-8 -*-
"""
Exceptions raised within or related to the ``newstore.config`` module
"""

from thick_denim.errors import ThickDenimError


class DictTraversalFailed(Exception):
    """raised when failed to traverse nested dicts with the given path
    """


class ThickDenimConfigException(ThickDenimError):
    """base-class for all exceptions raised by the module
    :py:mod:`newstore.config`"""


class UnsafeConfigMode(ThickDenimConfigException):
    """raised when a config file has wide permissions != 600"""

    def __init__(self, path, access_mode):
        self.path = path
        self.access_mode = access_mode
        super(UnsafeConfigMode, self).__init__(
            f"file {path} permissions' are too wide: '{access_mode}'. "
            f"Run this command to solve this problem: `chmod 600 {path}`"
        )


class NoConfigFound(ThickDenimConfigException):
    """raises when a configuration key lookup fails"""

    def __init__(self, msg):
        super().__init__(
            f"{msg}. Make sure to edit the toolbelt configuration according to the documentation."
        )


class InvalidConfigValue(ThickDenimConfigException):
    """raises when a configuration the type of a config value is unexpected"""
