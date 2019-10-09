# -*- coding: utf-8 -*-
"""
utility functions used within ``thick_denim.config``
mostly related to finding the optimum config file location
"""
# import sys
import os
import re

# import yaml

from pathlib import Path

# from datetime import datetime
# from tempfile import NamedTemporaryFile

from thick_denim.fs import absolute_path
from thick_denim.fs import determine_access_mode

from .errors import UnsafeConfigMode
from .errors import NoConfigFound


DEFAULT_LOOKUP_PATHS = ("~/.thick_denim.yml", "/etc/thick_denim.yml")


email_regex = re.compile(r"^(?P<username>[\w._+-]+)[@](?P<hostname>[\w_.-]+)")


def parse_email_address(email):
    found = email_regex.search(email)
    if found:
        return found.groupdict()

    return {}


def find_first_existing_path(lookup_paths) -> Path:
    """looks for the first existing config file based on the given lookup paths
    """
    for path in filter(
        lambda path: path.exists(),
        map(absolute_path, filter(bool, lookup_paths)),
    ):
        return Path(path)

    potential_paths = ", ".join(map(str, lookup_paths))

    raise NoConfigFound(
        f"Could not find a thick_denim-toolbelt config file in "
        f"any of the potential paths: {potential_paths}"
    )


def get_all_potential_lookup_paths():
    paths = [get_default_config_filename()]
    paths.extend(DEFAULT_LOOKUP_PATHS)
    return list(filter(bool, paths))


def guess_config_path():
    lookup_paths = get_all_potential_lookup_paths()
    path = find_first_existing_path(lookup_paths)
    access_mode = determine_access_mode(path)
    if access_mode != "600":
        raise UnsafeConfigMode(path, access_mode)

    return path


def get_default_config_filename():
    return os.getenv("THICK_DENIM_CONFIG_PATH") or "~/.thick_denim.yml"


def write_basic_config_file(destination: str = None) -> Path:
    destination = Path(
        destination or get_default_config_filename()
    ).expanduser()

    # ensure that parent dir exists
    destination.parent.mkdir(parents=True, exist_ok=True)

    # write default config file
    with destination.open("w") as fd:
        fd.write(BASIC_CONFIG)

    # fix permissions
    destination.chmod(0o600)
    return destination


BASIC_CONFIG = """
debug: no
verbose: yes

jira:
  accounts:
    goodscloud:
      token: SOMETOKEN  # get one at https://id.atlassian.com/manage/api-tokens
      server: https://goodscloud.atlassian.net
"""
