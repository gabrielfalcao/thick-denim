# -*- coding: utf-8 -*-
"""
file-system utilities module
"""

import pathlib

from pathlib import Path
from .serialization import yaml

module_path = Path(__file__).parent
app_icon_path = module_path.joinpath("icon.png")


def absolute_path(path: str) -> Path:
    """expands the given path and returns its absolute value"""
    return Path(path).expanduser().absolute()


def determine_access_mode(path) -> str:
    """returns the octal access mode of a file"""
    mode = path.stat().st_mode
    return oct(mode)[-3:]


def load_yaml_data_from_path(path):
    """utility function that reads the given path and returns python data
    from its string contents.

    :param path: a :py:class:`~pathlib.Path` instance
    :returns data: a ``dict`` in most cases.
    :raises TypeError: if given argument is not a :py:class:`pathlib.Path`
    """
    if not isinstance(path, pathlib.Path):
        raise TypeError(
            f"load_yaml_data_from_path() takes a pathlib.Path as argument, got {path} instead"
        )

    with path.open("r") as fd:
        return yaml.load(fd)
