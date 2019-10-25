from thick_denim.meta import (
    is_builtin_class_except,
    metaclass_declaration_contains_required_attribute,
)


TOKENS = []


def is_builtin_token(target: type) -> bool:
    """returns ``True`` if the given type is a token subclass"""

    return is_builtin_class_except(target, ["MetaToken", "Token"])


def validate_token_declaration(cls, name, attrs):
    """validates token class definitions"""
    target = f"{cls}.pattern"

    if not is_builtin_token(cls):
        return

    pattern = metaclass_declaration_contains_required_attribute(
        cls, name, attrs, "pattern", str
    )

    return pattern


class MetaToken(type):
    """metaclass for tokens
    """

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if is_builtin_token(cls):
            return

        pattern = validate_token_declaration(cls, name, attrs)
        TOKENS.append((pattern, cls))


class Token(metaclass=MetaToken):
    def __init__(self, value):
        self.type = self.__class__.__name__
        self.value = value

    def __repr__(self):
        return f'{self.type}({self.value!r})'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return (
            self.type == other.type
        ) and (
            self.value == other.value
        )

    def is_a(self, ttype: type):
        return isinstance(self, ttype)


class BaseParser(object):
    def __init__(self, stream):
        self.stream = stream
        self.start = 0
        self.position = 0
        self.width = 0

    def proceed(self):
        """scans the next character

        if the current position >= length of stream, sets width to 0
        else:
        - sets width to 1
        - increments current position

        :returns: the scanned item
        """
        if self.position >= len(self.stream):
            self.width = 0
            return  # EOF

        proceeditem = self.stream[self.position]
        self.width = 1
        self.position += self.width
        return proceeditem

    def reset(self):
        """sets the start to the current position"""
        self.start = self.position

    def retreat(self, steps=1):
        """rewinds the current position"""
        self.position -= self.width * steps

    def peek(self):
        """peeks at the next item without changing position"""
        value = self.proceed()
        self.retreat()

        return value

    def accept(self, valid):
        if self.proceed() in valid:
            return True
        self.retreat()
        return False

    def value(self):
        return self.stream[self.start:self.position]
