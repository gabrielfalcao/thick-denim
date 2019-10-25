class tokens:
    class OPEN_OBJ:
        char = "{"

    class CLOSE_OBJ:
        char = "}"


class Tokenizer(object):
    def __init__(self):
        self.state = []

    def feed(self, chars: str):
        self.state.extend(chars)

    def iter_parse(self):
        for char in self.state:
            token = None
            if char == "{":
                token = tokens.OPEN_OBJ
            elif char == "}":
                token = tokens.CLOSE_OBJ

            yield token

    def parse(self):
        return list(self.iter_parse())
