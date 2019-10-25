# -*- coding: utf-8; -*-

# {user={email="gabriel@nacaolivre.org", username=gabrielfalcao},
#  auth_token=bUpyTGNTUHJ4ZE96UHw8d3cK, meta={repos=10}}

NAMES = (
    'TOKEN_EOF',
    'TOKEN_BEGIN_OBJ',
    'TOKEN_NEWLINE',
    'TOKEN_TEXT',
    'TOKEN_COMMENT',
    'TOKEN_META_LABEL',
    'TOKEN_META_VALUE',
    'TOKEN_LABEL',
    'TOKEN_TABLE_COLUMN',
    'TOKEN_QUOTES',
    'TOKEN_TAG',
    'TOKEN_END_OBJ',
)

TOKENS = (
    TOKEN_EOF,           # 0
    TOKEN_BEGIN_OBJ,     # 1
    TOKEN_NEWLINE,       # 2
    TOKEN_TEXT,          # 3
    TOKEN_COMMENT,       # 4
    TOKEN_META_LABEL,    # 5
    TOKEN_META_VALUE,    # 6
    TOKEN_LABEL,         # 7
    TOKEN_TABLE_COLUMN,  # 8
    TOKEN_QUOTES,        # 9
    TOKEN_TAG,           # 10
    TOKEN_END_OBJ,       # 11
) = range(12)


TOKS = dict(enumerate(NAMES))


def tokname(index):
    name = TOKS.get(index)
    return name


class BaseParser(object):
    def __init__(self, stream):
        print(f'\n{self.__class__.__name__}({stream!r})')
        self.stream = stream
        self.start = 0
        self.position = 0
        self.width = 0

    def proceed(self):
        print(f'{self.__class__.__name__}.proceed()')
        if self.position >= len(self.stream):
            self.width = 0
            print(f' └─width = 0')
            return None  # EOF

        proceeditem = self.stream[self.position]
        self.width = 1
        self.position += self.width
        # print(f' ├─width = {self.width!r}')
        print(f' └─position = {self.position!r}')
        return proceeditem

    def ignore(self):
        print(f'{self.__class__.__name__}.ignore()')
        self.start = self.position
        print(f'{self.__class__.__name__}.start = {self.start}')

    def retreat(self, steps=1):
        print(f'{self.__class__.__name__}.retreat(steps={steps})')
        self.position -= self.width * steps
        print(f'{self.__class__.__name__}.position = {self.position}')

    def peek(self):
        print(f'{self.__class__.__name__}.peak()')
        value = self.proceed()
        self.retreat()
        print(f'{self.__class__.__name__}.peek() -> {value!r}')
        return value

    def accept(self, valid):
        print(f'{self.__class__.__name__}.accept(valid={valid!r})')
        if self.proceed() in valid:
            print(f'{self.__class__.__name__}.accept([])) -> True')
            return True
        self.retreat()
        print(f'{self.__class__.__name__}.accept([])) -> False')
        return False


class Lexer(BaseParser):
    def __init__(self, stream):
        super(Lexer, self).__init__(stream)
        self.current_line = 1
        self.tokens = []

    def emit(self, token, strip=False):
        print(f'{self.__class__.__name__}.emit({tokname(token)}, strip={strip})')
        value = self.stream[self.start:self.position]
        if strip:
            value = value.strip()
        self.tokens.append((self.current_line, token, value))
        self.start = self.position

    def emit_s(self, token, strip=False):
        print(f'{self.__class__.__name__}.emit_s()')
        if self.position > self.start:
            self.emit(token, strip)

    def run(self):
        print(f'{self.__class__.__name__}.run()')
        state = self.lex_obj
        while state:
            state = state()
        return self.tokens

    def match_quotes(self, cursor):
        print(f'{self.__class__.__name__}.match_quotes()')
        stream_at_cursor = self.stream[self.position:]
        return cursor in ('"', "'") and (
            stream_at_cursor.startswith('""')
            or stream_at_cursor.startswith("''")
        )

    def lex_field(self):
        print(f'{self.__class__.__name__}.lex_field()')
        while True:
            cursor = self.proceed()
            if cursor is None:  # EOF
                break
            elif cursor == "\n":
                self.retreat()
                return self.lex_obj
            elif cursor == "|":
                self.retreat()
                self.emit_s(TOKEN_TABLE_COLUMN, strip=True)
                return self.lex_obj
        return self.lex_obj

    def lex_comment(self):
        print(f'{self.__class__.__name__}.lex_comment()')
        while True:
            cursor = self.proceed()
            if cursor is None:  # EOF
                break
            elif cursor == "\n":
                self.retreat()
                break
            elif cursor == ":":
                self.retreat()
                self.emit(TOKEN_META_LABEL)
                self.proceed()
                self.ignore()
                return self.lex_comment_metadata_value
        self.emit_s(TOKEN_COMMENT)
        return self.lex_obj

    def lex_comment_metadata_value(self):
        print(f'{self.__class__.__name__}.lex_comment_metadata_value()')
        while True:
            cursor = self.proceed()
            if cursor is None or cursor == "\n":
                self.retreat()
                self.emit_s(TOKEN_META_VALUE)
                return self.lex_obj

    def lex_quotes(self):
        print(f'{self.__class__.__name__}.lex_quotes()')
        internal_lines = 0
        while True:
            cursor = self.proceed()
            if self.match_quotes(cursor):
                # Consume all the text inside of the quotes
                self.retreat()
                self.emit_s(TOKEN_TEXT)
                self.current_line += internal_lines

                # Consume the closing quotes
                for _ in range(3):
                    self.accept(['"', "'"])
                self.emit_s(TOKEN_QUOTES)
                break
            elif cursor == "\n":
                internal_lines += 1
        return self.lex_obj

    def lex_tag(self):
        print(f'{self.__class__.__name__}.lex_tag()')
        while True:
            cursor = self.proceed()
            if cursor is None:  # EOF
                break
            elif cursor in (" ", "\n"):
                self.retreat()
                break
        self.emit_s(TOKEN_TAG)
        return self.lex_obj

    def lex_obj(self):
        print(f'{self.__class__.__name__}.lex_obj()')
        while True:
            cursor = self.proceed()
            if cursor is None:  # EOF
                break
            elif cursor == ":":
                self.retreat()
                self.emit_s(TOKEN_LABEL)
                self.proceed()
                self.ignore()
                return self.lex_obj
            elif cursor == "#":
                self.retreat()
                self.emit_s(TOKEN_TEXT)
                self.proceed()
                return self.lex_comment
            elif cursor == "|":
                self.ignore()
                return self.lex_field
            elif cursor == "@":
                self.ignore()
                return self.lex_tag
            elif cursor == "\n":
                self.retreat()
                self.emit_s(TOKEN_TEXT)
                self.proceed()
                self.emit_s(TOKEN_NEWLINE)
                self.current_line += 1
                return self.lex_obj
            elif self.match_quotes(cursor):
                for _ in range(2):
                    self.accept(['"', "'"])
                self.emit_s(TOKEN_QUOTES)
                return self.lex_quotes

        self.emit_s(TOKEN_TEXT)
        self.emit(TOKEN_EOF)
        return None


class Parser(BaseParser):
    def __init__(self, stream):
        super(Parser, self).__init__(stream)
        self.output = []
        self.encoding = "utf-8"
        self.language = "en"
        self.languages = {"en": {}}

    def accept(self, valid):
        _, token, value = self.proceed()
        if (token, value) in valid:
            return True
        self.retreat()
        return False

    def proceed(self):
        """Same as BaseParser.proceed() but returns (None, None)
        instead of None on EOF"""
        output = super(Parser, self).proceed()
        return (None, None, None) if output is None else output

    def match_label(self, type_, label):
        return self.languages[self.language][type_].match(label)

    def eat_newlines(self):
        count = 0
        while self.accept([(TOKEN_NEWLINE, "\n")]):
            self.ignore()
            count += 1
        return count

    def parse_title(self):
        "Parses the stream until token != TOKEN_TEXT than returns Text()"
        line, token, value = self.proceed()
        if token == TOKEN_TEXT:
            return Ast.Text(line=line, text=value)
        else:
            self.retreat()
            return None

    def parse_description(self):
        description = []
        start_line = -1
        while True:
            line, token, value = self.proceed()
            if not len(description):
                start_line = line
            if self.match_label("given", value):
                self.retreat()
                break
            elif token == TOKEN_TEXT:
                description.append(value)
            elif token == TOKEN_NEWLINE:
                self.ignore()
            else:
                self.retreat()
                break
        if description:
            return Ast.Text(line=start_line, text=" ".join(description))
        else:
            return None

    def parse_background(self):
        line, _, label = self.proceed()
        if not self.match_label("background", label):
            self.retreat()
            return None
        return Ast.Background(line, self.parse_title(), self.parse_steps())

    def parse_step_text(self):
        self.proceed()
        self.ignore()  # Skip enter QUOTES
        line, token, step_text = self.proceed()
        assert token == TOKEN_TEXT
        _, token, _ = self.proceed()  # Skip exit QUOTES
        assert token == TOKEN_QUOTES
        self.ignore()
        return Ast.Text(line=line, text=step_text)

    def parse_steps(self):
        steps = []
        while True:
            line, token, value = self.proceed()
            retreat = self.eat_newlines()
            _, proceedtoken, _ = self.peek()
            if token == TOKEN_NEWLINE:
                self.ignore()
            elif (
                token in (TOKEN_LABEL, TOKEN_TEXT)
                and proceedtoken == TOKEN_TABLE_COLUMN
                and not self.match_label("examples", value)
            ):
                steps.append(
                    Ast.Step(
                        line=line,
                        title=Ast.Text(line=line, text=value),
                        table=self.parse_table(),
                    )
                )
            elif (
                token in (TOKEN_LABEL, TOKEN_TEXT)
                and proceedtoken == TOKEN_QUOTES
            ):
                steps.append(
                    Ast.Step(
                        line=line,
                        title=Ast.Text(line=line, text=value),
                        text=self.parse_step_text(),
                    )
                )
            elif token == TOKEN_TEXT:
                steps.append(
                    Ast.Step(line=line, title=Ast.Text(line=line, text=value))
                )
            else:
                self.retreat(retreat + 1)
                break
        return steps

    def parse_table(self):
        table = []
        row = []
        start_line = -1
        while True:
            line, token, value = self.proceed()
            if not len(table):
                start_line = line
            if token == TOKEN_TABLE_COLUMN:
                row.append(value)
            elif token == TOKEN_NEWLINE:
                table.append(row)
                row = []
            else:
                self.retreat()
                break
        return Ast.Table(line=start_line, fields=table)

    def parse_examples(self):
        self.eat_newlines()
        tags = self.parse_tags()
        line, token, value = self.proceed()
        assert token == TOKEN_LABEL and self.match_label("examples", value)
        self.eat_newlines()
        return Ast.Examples(line=line, tags=tags, table=self.parse_table())

    def parse_scenarios(self):
        scenarios = []
        while True:
            self.eat_newlines()
            tags = self.parse_tags()

            line, token, value = self.proceed()
            if token in (None, TOKEN_EOF):
                break  # EOF
            elif self.match_label("scenario_outline", value):
                scenario = Ast.ScenarioOutline(line=line)
                scenario.tags = tags
                scenario.title = self.parse_title()
                scenario.description = self.parse_description()
                scenario.steps = self.parse_steps()
                scenario.examples = self.parse_examples()
            elif self.match_label("scenario", value):
                scenario = Ast.Scenario(line=line)
                scenario.tags = tags
                scenario.title = self.parse_title()
                scenario.description = self.parse_description()
                scenario.steps = self.parse_steps()
            else:
                raise SyntaxError(
                    (
                        "`{}' should not be declared here, "
                        "Scenario or Scenario Outline expected"
                    ).format(value)
                )
            scenarios.append(scenario)
        return scenarios

    def parse_tags(self):
        tags = []
        while True:
            line, token, value = self.proceed()
            if token == TOKEN_TAG:
                tags.append(value)
            elif token == TOKEN_NEWLINE:
                self.ignore()
            else:
                self.retreat()
                break
        return tags

    def parse_feature(self):
        feature = Ast.Feature()
        feature.tags = self.parse_tags()

        line, _, label = self.proceed()
        if not self.match_label("feature", label):
            raise SyntaxError(
                "Feature expected in the beginning of the file, "
                "found `{}' though.".format(label)
            )

        feature.line = line
        feature.title = self.parse_title()
        feature.description = self.parse_description()
        feature.background = self.parse_background()
        feature.scenarios = self.parse_scenarios()
        return feature

    def parse_metadata(self):
        line, token, key = self.proceed()
        if token in (None, TOKEN_EOF):
            return
        assert token == TOKEN_META_LABEL

        line, token, value = self.proceed()
        if token in (None, TOKEN_EOF):
            return
        elif token != TOKEN_META_VALUE:
            raise SyntaxError(
                "No value found for the meta-field `{}'".format(key)
            )
        return Ast.Metadata(line, key, value)


class Ast(object):
    class Node(object):
        def __eq__(self, other):
            return getattr(other, "__dict__", None) == self.__dict__

        def __repr__(self):
            fields = [
                "{}={}".format(x[0], repr(x[1])) for x in self.__dict__.items()
            ]
            return "{}({})".format(self.__class__.__name__, ", ".join(fields))

    class Metadata(Node):
        def __init__(self, line, key, value):
            self.line = line
            self.key = key
            self.value = value

    class Text(Node):
        def __init__(self, line, text):
            self.line = line
            self.text = text

    class Background(Node):
        def __init__(self, line, title=None, steps=None):
            self.line = line
            self.title = title
            self.steps = steps or []

    class Feature(Node):
        def __init__(
            self,
            line=None,
            title=None,
            tags=None,
            description=None,
            background=None,
            scenarios=None,
        ):
            self.line = line
            self.title = title
            self.tags = tags or []
            self.description = description
            self.background = background
            self.scenarios = scenarios or []

    class Scenario(Node):
        def __init__(
            self, line, title=None, tags=None, description=None, steps=None
        ):
            self.line = line
            self.title = title
            self.tags = tags or []
            self.description = description
            self.steps = steps or []

    class ScenarioOutline(Node):
        def __init__(
            self,
            line,
            title=None,
            tags=None,
            description=None,
            steps=None,
            examples=None,
        ):
            self.line = line
            self.title = title
            self.tags = tags or []
            self.description = description
            self.steps = steps or []
            self.examples = examples

    class Step(Node):
        def __init__(self, line, title, table=None, text=None):
            self.line = line
            self.title = title
            self.table = table
            self.text = text

    class Table(Node):
        def __init__(self, line, fields):
            self.line = line
            self.fields = fields

    class Examples(Node):
        def __init__(self, line, tags=None, table=None):
            self.line = line
            self.tags = tags or []
            self.table = table
