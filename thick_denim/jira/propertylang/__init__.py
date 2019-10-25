from .lexer import Parser, Lexer


def parse_properties(string: str):
    lexer = Lexer(string)
    lexer.run()
    return Parser(lexer.tokens).run()
