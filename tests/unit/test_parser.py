# -*- coding: utf-8; -*-

from thick_denim.jira.propertylang import ast, lexer
from thick_denim.jira.propertylang.lexer import Parser


def test_parse_simple_kv():
    "run() Should be able to find text before EOF"

    # Given a parser with lexemes that represent a simple object
    parser = Parser([
        lexer.TOKEN_OBJECT_START("{"),
        lexer.TOKEN_KEY("foo"),
        lexer.TOKEN_VALUE("bar"),
        lexer.TOKEN_OBJECT_END("}"),
        lexer.TOKEN_EOF(""),
    ])

    # When I run the parser
    parser.run()

    # Then the ast should have an object


def test_parse_object_with_siblings():
    "run() Should be able to find siblings before EOF"

    # Given a parser with lexemes that represent a simple object
    parser = Parser([
        lexer.TOKEN_OBJECT_START("{"),
        lexer.TOKEN_KEY("foo"),
        lexer.TOKEN_VALUE("bar"),
        lexer.TOKEN_SEPARATOR(", "),
        lexer.TOKEN_KEY("chuck"),
        lexer.TOKEN_VALUE("norris"),
        lexer.TOKEN_OBJECT_END("}"),
        lexer.TOKEN_EOF(""),
    ])

    # When I run the parser
    parser.run()

    # Then the ast should have an object
