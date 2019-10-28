# -*- coding: utf-8; -*-

from thick_denim.jira.propertylang import ast, lexer
from thick_denim.jira.propertylang.lexer import Lexer


def test_lex_test_eof():
    "Lexer.run() should parse an empty string"

    # Given a lexer with an empty string
    parser = Lexer("")

    # When I run the lexer
    parser.run()

    # Then we see we've got to EOF and that new state is nil
    parser.tokens.should.equal([lexer.TOKEN_EOF("")])


def test_lex_empty_obj():
    "Lexer.run() should parse {}"

    # Given a lexer that takes some text as input an empty object
    parser = Lexer("{}")

    # When I run the lexer
    parser.run()

    # Then we see we found both the text and the EOF token
    parser.tokens.should.equal([
        lexer.TOKEN_OBJECT_START("{"),
        lexer.TOKEN_OBJECT_END("}"),
        lexer.TOKEN_EOF(""),
    ])



# def test_lex_text():
#     "Lexer.run() should parse an dummy string"

#     # Given a lexer that takes some text as input string
#     parser = Lexer("some text")

#     # When I run the lexer
#     parser.run()

#     # Then we see we found both the text and the EOF token
#     parser.tokens.should.equal([
#         lexer.TOKEN_KEY("some text"),
#         lexer.TOKEN_EOF(""),
#     ])


def test_lex_obj():
    "Lexer.run() should parse {foo=bar}"

    # Given a lexer that takes some text as input string
    parser = Lexer("{foo=bar}")

    # When I run the lexer
    parser.run()

    # Then we see we found both the text and the EOF token
    parser.tokens.should.equal([
        lexer.TOKEN_OBJECT_START("{"),
        lexer.TOKEN_KEY("foo"),
        lexer.TOKEN_VALUE("bar"),
        lexer.TOKEN_OBJECT_END("}"),
        lexer.TOKEN_EOF(""),
    ])


def test_lex_obj_sibling():
    "Lexer.run() should parse {foo=bar, chuck=norris}"

    # Given a lexer that takes some text as input string
    parser = Lexer("{foo=bar, chuck=norris}")

    # When I run the lexer
    parser.run()

    # Then we see we found both the text and the EOF token
    parser.tokens.should.equal([
        lexer.TOKEN_OBJECT_START("{"),
        lexer.TOKEN_KEY("foo"),
        lexer.TOKEN_VALUE("bar"),
        lexer.TOKEN_SEPARATOR(", "),
        lexer.TOKEN_KEY("chuck"),
        lexer.TOKEN_VALUE("norris"),
        lexer.TOKEN_OBJECT_END("}"),
        lexer.TOKEN_EOF(""),
    ])


def test_lex_obj_sub_obj():
    "Lexer.run() should parse {user={name=foo, age=22}}"

    # Given a lexer that takes some text as input string
    parser = Lexer("{user={name=foo, age=22}}")

    # When I run the lexer
    parser.run()

    # Then we see we found both the text and the EOF token
    parser.tokens.should.equal([
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


def test_lex_obj_obj_with_datetime():
    'Lexer.run() should parse {datetime="2019-10-25 03:06:44"}'

    # Given a lexer that takes some text as input string
    parser = Lexer('{datetime="2019-10-25 03:06:44"}')

    # When I run the lexer
    parser.run()

    # Then we see we found both the text and the EOF token
    parser.tokens.should.equal([
        lexer.TOKEN_OBJECT_START("{"),
        lexer.TOKEN_KEY("datetime"),
        lexer.TOKEN_VALUE('2019-10-25 03:06:44'),
        lexer.TOKEN_OBJECT_END("}"),
        lexer.TOKEN_EOF(""),
    ])


def test_lex_obj_obj_with_json():
    'Lexer.run() should parse {datetime="2019-10-25 03:06:44", user={"name": "chuck", "age": "NaN"}}'

    # Given a lexer that takes some text as input string
    parser = Lexer('{datetime="2019-10-25 03:06:44", user={"name": "chuck", "age": "NaN"}}')

    # When I run the lexer
    parser.run()

    # Then we see we found both the text and the EOF token
    parser.tokens.should.equal([
        lexer.TOKEN_OBJECT_START("{"),
        lexer.TOKEN_KEY("datetime"),
        lexer.TOKEN_VALUE('2019-10-25 03:06:44'),
        lexer.TOKEN_SEPARATOR(", "),
        lexer.TOKEN_KEY("user"),
        lexer.TOKEN_OBJECT_START("{"),
        lexer.TOKEN_KEY("name"),
        lexer.TOKEN_VALUE("chuck"),
        lexer.TOKEN_SEPARATOR(", "),
        lexer.TOKEN_KEY("age"),
        lexer.TOKEN_VALUE("NaN"),
        lexer.TOKEN_OBJECT_END("}"),
        lexer.TOKEN_OBJECT_END("}"),
        lexer.TOKEN_EOF(""),
    ])
