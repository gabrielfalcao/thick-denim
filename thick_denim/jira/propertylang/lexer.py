# -*- coding: utf-8; -*-
from .base import Token, BaseParser
from . import ast
# {user={email="gabriel@nacaolivre.org", username=gabrielfalcao},
#  auth_token=bUpyTGNTUHJ4ZE96UHw8d3cK, meta={repos=10}}


def strip_quotes(string: str):
    return string.strip('"')


class TOKEN_EOF(Token):
    pattern = ''


class TOKEN_KEY(Token):
    pattern = r'\w+'


class TOKEN_TEXT(Token):
    pattern = r'\w+'


class TOKEN_VALUE(Token):
    pattern = r'\w+'


class TOKEN_OBJECT_START(Token):
    pattern = '{'


class TOKEN_OBJECT_END(Token):
    pattern = '{'


class TOKEN_OBJECT(Token):
    pattern = '{}'


class TOKEN_SEPARATOR(Token):
    pattern = ','


class Lexer(BaseParser):
    def __init__(self, stream):
        super(Lexer, self).__init__(stream)
        self.tokens = []

    def emit(self, token, strip=False):
        value = self.value()
        if strip:
            value = value.strip()
        self.tokens.append(token(value))
        self.start = self.position

    def emit_s(self, token, strip=False):
        if self.position > self.start:
            self.emit(token, strip)

    def run(self):
        state = self.lex_obj
        while state:
            state = state()
        return self.tokens

    def lex_obj(self):
        while True:
            cursor = self.proceed()
            if cursor is None:  # EOF
                break
            elif cursor == "{":
                self.emit_s(TOKEN_OBJECT_START)
                self.proceed()
            elif cursor in ('"', "'"):
                self.reset()
                self.lex_value()
                continue

            elif cursor == "}":
                self.retreat()
                self.emit_s(TOKEN_VALUE)
                self.proceed()
                self.emit_s(TOKEN_OBJECT_END)
            elif cursor in ("=", ":"):
                self.retreat()
                self.emit_s(TOKEN_KEY)
                self.proceed()
                self.reset()
            elif cursor == ",":
                self.retreat()
                self.emit_s(TOKEN_VALUE)
                self.proceed()
                if self.peek() == ' ':
                    self.proceed()
                self.emit_s(TOKEN_SEPARATOR)

        self.emit_s(TOKEN_KEY)
        self.emit(TOKEN_EOF)
        return None

    def lex_value(self):
        while True:
            cursor = self.proceed()
            if cursor is None:  # EOF
                break
            elif cursor == '"':
                self.retreat()
                self.emit_s(TOKEN_VALUE)
                self.proceed()
                self.reset()
                break

        return None


class Parser(BaseParser):
    def __init__(self, stream):
        super(Parser, self).__init__(stream)
        self.data = None
        self.stack = []
        self.keys = []

    def run(self):
        state = self.parse_obj
        while state:
            state = state()
        return self.data

    def parse_obj(self):
        token = self.peek()
        while not token.is_a(TOKEN_EOF):
            token = self.proceed()
            if token is None:
                break

            if token.is_a(TOKEN_OBJECT_START):
                self.stack.append({})
                continue

            elif token.is_a(TOKEN_KEY):
                key = strip_quotes(token.value)
                self.keys.append(key)
                continue

            elif token.is_a(TOKEN_VALUE):
                self.keys.pop(-1)
                self.stack[-1][key] = strip_quotes(token.value)
                continue

            elif token.is_a(TOKEN_SEPARATOR):
                continue
            elif token.is_a(TOKEN_OBJECT_END):
                if self.keys:
                    key = self.keys.pop(-1)
                    data = self.stack.pop(-1)
                    self.stack.append({key: data})
                continue

        self.data = self.stack[-1]
        return None
