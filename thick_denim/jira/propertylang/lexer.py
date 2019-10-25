# -*- coding: utf-8; -*-
import re
from .base import Token, BaseParser, TOKENS
# {user={email="gabriel@nacaolivre.org", username=gabrielfalcao},
#  auth_token=bUpyTGNTUHJ4ZE96UHw8d3cK, meta={repos=10}}


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

    def value(self):
        return self.stream[self.start:self.position]

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
            value = self.value()
            if cursor is None:  # EOF
                break
            elif cursor == "{":
                self.emit_s(TOKEN_OBJECT_START)
                self.proceed()
            elif cursor == "}":
                self.retreat()
                self.emit_s(TOKEN_VALUE)
                self.proceed()
                self.emit_s(TOKEN_OBJECT_END)
            elif cursor == "=":
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

            # elif cursor == "}":
            #     self.reset()
            #     self.emit_s(TOKEN_VALUE)
            #     self.proceed()
            #     self.reset()
            #     return self.lex_obj
            # elif cursor == "=":
            #     self.retreat()
            #     self.emit_s(TOKEN_KEY)
            #     self.proceed()
            #     self.reset()

            # elif cursor == ",":
            #     cursor = self.proceed()
            #     if cursor == " ":
            #         self.emit_s(TOKEN_KEY)
            #         self.proceed()
            #     else:
            #         self.retreat()
            #         self.emit_s(TOKEN_VALUE)
            #         return self.lex_value

        self.emit_s(TOKEN_OBJECT)
        self.emit(TOKEN_EOF)
        return None

    def lex_value(self):
        while True:
            cursor = self.proceed()
            if cursor is None:  # EOF
                break
            elif cursor == "=":
                self.proceed()
                self.reset()
                continue
            elif cursor == "}":
                self.retreat()
                return self.lex_obj
            elif cursor == "{":
                self.retreat()
                self.emit(TOKEN_VALUE)
                self.proceed()
                self.ignore()
                return self.lex_obj

        self.emit_s(TOKEN_VALUE)
        return self.lex_obj

    def lex_key(self):
        while True:
            cursor = self.proceed()
            if cursor is None:  # EOF
                break

            elif cursor == "}":
                self.retreat()
                return self.lex_obj
            elif cursor == "{":
                self.retreat()
                self.emit(TOKEN_VALUE)
                self.proceed()
                self.ignore()
                return self.lex_obj

        self.emit_s(TOKEN_VALUE)
        return self.lex_obj
