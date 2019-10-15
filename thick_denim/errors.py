"""
contains the base classes for all other internal exceptions.
"""


class ThickDenimError(Exception):
    """base exception for all exceptions in the module's domain.

    Exceptions of this type don't print full traceback, instead an ansi-colored error message on STDERR.

    Make sure to put all important debug information in the error message :)
    """


class ThickDenimModelError(Exception):
    """exception for errors happening inside of ``thick_denim.base.Model``"""
