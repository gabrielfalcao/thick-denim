# -*- coding: utf-8 -*-
"""
contains a yaml abstraction that can keep comments when rewriting configs
"""
import io
from ruamel.yaml import YAML


def get_parser():
    """returns a ruamel.yaml parser pre-configured"""
    parser = YAML(typ="rt")  # "round-trip" parsing type keep
    # comments, this is important

    parser.default_flow_style = False  # dump as yaml, not json
    return parser


class yaml:
    """utility to parse and serialize YAML. Interface is compatible with :py:mod:`json`."""

    @classmethod
    def load(cls, *args, **kw):
        """parse YAML from a file-like object"""
        return get_parser().load(*args, **kw)

    @classmethod
    def dump(cls, *args, **kw):
        """serialize YAML into a file-like object"""
        return get_parser().dump(*args, **kw)

    @classmethod
    def loads(cls, string):
        """parse YAML from a string"""
        buf = io.String(string)
        return cls.load(buf)

    @classmethod
    def dumps(cls):
        """serialize YAML into a string"""
        buf = io.String()
        cls.dump(buf)
        return buf.getvalue()
