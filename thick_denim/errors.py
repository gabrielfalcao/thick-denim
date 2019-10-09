"""
contains the base classes for all other internal exceptions.
"""


class ThickDenimError(Exception):
    """base exception for all exceptions in the module's domain"""


class ThickDenimModelError(Exception):
    """exception for errors happening inside of ``thick_denim.base.Model``"""
