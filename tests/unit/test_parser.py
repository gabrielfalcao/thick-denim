# -*- coding: utf-8; -*-

from thick_denim.jira.propertylang import ast, lexer
from thick_denim.jira.propertylang.lexer import Parser


def test_parse_simple_kv():
    "Parser.run() should parse a grammar of lexemes that represent a simple object"

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
    parser.data.should.equal({
        "foo": "bar"
    })


def test_parse_object_with_siblings():
    "Parser.run() should parse a grammar of lexemes that represent a simple object with siblings"

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
    parser.data.should.equal({
        "foo": "bar",
        "chuck": "norris",
    })


def test_parse_nested_object_with_siblings():
    "Parser.run() should parse a grammar of lexemes that represent a nested object"

    # Given a parser with lexemes that represent a simple object
    parser = Parser([
        lexer.TOKEN_OBJECT_START("{"),
        lexer.TOKEN_KEY("user"),
        lexer.TOKEN_OBJECT_START("{"),
        lexer.TOKEN_KEY("name"),
        lexer.TOKEN_VALUE("foo"),
        lexer.TOKEN_SEPARATOR(", "),
        lexer.TOKEN_KEY("age"),
        lexer.TOKEN_VALUE("22"),
        lexer.TOKEN_OBJECT_END("}"),
        lexer.TOKEN_OBJECT_END("}"),
        lexer.TOKEN_EOF(""),
    ])

    # When I run the parser
    parser.run()

    # Then the ast should have an object
    parser.data.should.equal({
        "user": {
            "name": "foo",
            "age": "22",
        }
    })
