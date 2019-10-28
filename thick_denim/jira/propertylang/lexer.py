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
        print(f'emit({token}) = {value!r}')

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
        TOKEN_TEXT = TOKEN_KEY
        within_quotes = None
        while True:
            cursor = self.proceed()
            value = self.value()
            if cursor is None:  # EOF
                break
            elif cursor == "{":
                self.emit(TOKEN_OBJECT_START)
                TOKEN_TEXT = TOKEN_KEY
            elif cursor == "}":
                if value != cursor:
                    self.retreat()
                    self.emit_s(TOKEN_TEXT)
                    self.proceed()
                self.emit(TOKEN_OBJECT_END)
                continue
            elif cursor in ("=", ":"):
                if within_quotes:
                    continue
                self.retreat()
                if TOKEN_TEXT == TOKEN_KEY:
                    self.emit(TOKEN_KEY)
                    TOKEN_TEXT = TOKEN_VALUE
                else:
                    self.emit(TOKEN_VALUE)
                    TOKEN_TEXT = TOKEN_KEY

                self.proceed()
                self.reset()

            elif cursor in ('"', "'"):
                if not within_quotes:
                    within_quotes = cursor
                    self.reset()
                elif within_quotes != cursor:
                    continue
                else:
                    self.retreat()
                    self.emit_s(TOKEN_TEXT)
                    self.proceed()
                    self.reset()
                    within_quotes = None

            elif cursor == ",":
                if value != cursor:
                    self.retreat()
                    self.emit_s(TOKEN_TEXT)
                    self.proceed()
                if self.peek() == ' ':
                    self.proceed()
                self.emit_s(TOKEN_SEPARATOR)
                if TOKEN_TEXT == TOKEN_KEY:
                    TOKEN_TEXT = TOKEN_VALUE
                else:
                    TOKEN_TEXT = TOKEN_KEY

        self.emit_s(TOKEN_TEXT)
        self.emit(TOKEN_EOF)
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
