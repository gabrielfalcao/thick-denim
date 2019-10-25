# -*- coding: utf-8; -*-

from thick_denim.jira.propertylang import ast, lexer
from thick_denim.jira.propertylang.lexer import Lexer


def test_lex_test_eof():
    "run() Should be able to find EOF"

    # Given a lexer with an empty string
    parser = Lexer("")

    # When I run the lexer
    parser.run()

    # Then we see we've got to EOF and that new state is nil
    parser.tokens.should.equal([lexer.TOKEN_EOF("")])


def test_lex_text():
    "run() Should be able to find text before EOF"

    # Given a lexer that takes some text as input string
    parser = Lexer("some text")

    # When I run the lexer
    parser.run()

    # Then we see we found both the text and the EOF token
    parser.tokens.should.equal([
        lexer.TOKEN_OBJECT("some text"),
        lexer.TOKEN_EOF(""),
    ])


def test_lex_obj():
    "run() Should be able to find text before EOF"

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
    "run() Should be able to find siblings before EOF"

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
