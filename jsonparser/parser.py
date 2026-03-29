from enum import Enum
from typing import List, Optional, Dict
from dataclasses import dataclass
from abc import ABC, abstractmethod


JSON = Dict | List | str | int | float | bool

# Tokens


class TokenType(Enum):
    # symbols
    LEFT_PARENTHESIS = "LEFT_PARENTHESIS"
    RIGHT_PARENTHESIS = "RIGHT_PARENTHESIS"
    LEFT_BRACKET = "LEFT_BRACKET"
    RIGHT_BRACKET = "RIGHT_BRACKET"
    COLON = "COLON"
    COMMA = "COMMA"

    # primitives
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"


@dataclass
class Token:
    type: TokenType
    lexme: str
    literal: Optional[object] = None


def is_digit(char: str):
    assert len(char) == 1
    return char in "0123456789"


def is_lowercase_alpha(char):
    return "a" <= char <= "z"


class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1

    def is_at_end(self):
        """Returns True if the scanner has reached the end of source, otherwise False"""
        return self.current >= len(self.source)

    def advance(self) -> str:
        """
        Move current pointer ahead by 1

        Returns:
            str: returns the char at the previous current pointer
        """
        current = self.current
        self.current += 1
        return self.source[current]

    def scan_token(self):
        char = self.advance()

        if char == "{":
            self.tokens.append(Token(type=TokenType.LEFT_PARENTHESIS, lexme=char))
        elif char == "}":
            self.tokens.append(Token(type=TokenType.RIGHT_PARENTHESIS, lexme=char))
        elif char == "[":
            self.tokens.append(Token(TokenType.LEFT_BRACKET, char))
        elif char == "]":
            self.tokens.append(Token(TokenType.RIGHT_BRACKET, char))
        elif char == ":":
            self.tokens.append(Token(type=TokenType.COLON, lexme=char))
        elif char == ",":
            self.tokens.append(Token(type=TokenType.COMMA, lexme=char))
        elif char == '"':
            self.scan_string()
        elif is_digit(char):
            self.scan_number()
        elif char in {"t", "f"}:
            self.scan_boolean()
        elif char == "\n":
            return

    def scan_string(self):
        # stop at the char "
        while self.peek() != '"':
            self.advance()

        # consume the char, now 1 index ahead of "
        self.advance()

        string = self.source[self.start : self.current]
        self.tokens.append(
            Token(
                type=TokenType.STRING,
                lexme=string,
                literal=string[1:-1],  # remove the starting and end quotes
            )
        )

    def scan_number(self):
        # TODO: refactor below
        # do not advance if we're at the end of source
        while not self.is_at_end() and is_digit(self.peek()):
            self.advance()

        if not self.is_at_end() and self.peek() == "." and is_digit(self.peek(1)):
            self.advance()
            while not self.is_at_end() and is_digit(self.peek()):
                self.advance()

        lexme = self.get_lexme()

        if "." in lexme:
            literal = float(lexme)
        else:
            literal = int(lexme)

        self.tokens.append(Token(type=TokenType.NUMBER, lexme=lexme, literal=literal))

    def scan_boolean(self):
        while not self.is_at_end() and is_lowercase_alpha(self.peek()):
            self.advance()

        lexme = self.get_lexme()
        assert lexme in {"true", "false"}

        literal = True if lexme == "true" else False
        self.tokens.append(Token(type=TokenType.BOOLEAN, lexme=lexme, literal=literal))

    def peek(self, n: int = 0):
        return self.source[self.current + n]

    def get_lexme(self):
        return self.source[self.start : self.current]

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        return self.tokens


# AST Nodes


@dataclass
class JSONNode(ABC):

    @abstractmethod
    def eval(self) -> JSON: ...


@dataclass
class JSONString:
    value: str

    def eval(self) -> JSON:
        return self.value

    # JSONString is hashable - implements __hash__ and __eq__
    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other: "JSONString"):
        return self.value == other.value


@dataclass
class JSONNumber:
    value: int | float

    def eval(self) -> JSON:
        return self.value


@dataclass
class JSONBoolean:
    value: bool

    def eval(self) -> JSON:
        return self.value


@dataclass
class JSONDict:
    value: dict[JSONString, JSONNode]

    def eval(self) -> JSON:
        return {k.eval(): v.eval() for k, v in self.value.items()}


@dataclass
class JSONList:
    value: list[JSONNode]

    def eval(self) -> JSON:
        return [node.eval() for node in self.value]


def is_primitive(token: Token):
    return token.type in {TokenType.STRING, TokenType.NUMBER, TokenType.BOOLEAN}


def build_primitive_ast(tokens: list[Token]):
    token = tokens[0]
    type_to_ast_node = {
        TokenType.STRING: JSONString,
        TokenType.NUMBER: JSONNumber,
        TokenType.BOOLEAN: JSONBoolean,
    }
    return type_to_ast_node[token.type](token.literal)


def build_ast(tokens: list[Token]) -> JSONNode:
    # base case: primitives string, number, boolean
    if len(tokens) == 1:
        return build_primitive_ast(tokens)

    # parse json dict or list
    if len(tokens) >= 2:
        first_token = tokens[0]
        last_token = tokens[-1]

        if (
            first_token.type == TokenType.LEFT_PARENTHESIS
            and last_token.type == TokenType.RIGHT_PARENTHESIS
        ):
            return build_dict_ast(tokens)

        if (
            first_token.type == TokenType.LEFT_BRACKET
            and last_token.type == TokenType.RIGHT_BRACKET
        ):
            return build_list_ast(tokens)


def find_closing_token(tokens: list[Token], start: int):
    """
    Find the index of the closing right parenthesis or bracket depending on
    `tokens[start]`.
    """
    first_token = tokens[start]
    assert first_token.type in {
        TokenType.LEFT_PARENTHESIS,
        TokenType.LEFT_BRACKET,
    }

    counter = 1
    i = start + 1

    while counter != 0 and i < len(tokens):
        token = tokens[i]
        if token.type == TokenType.LEFT_PARENTHESIS:
            counter += 1
        elif token.type == TokenType.RIGHT_PARENTHESIS:
            counter -= 1
        elif token.type == TokenType.LEFT_BRACKET:
            counter += 1
        elif token.type == TokenType.RIGHT_BRACKET:
            counter -= 1

        i += 1

    # i is 1 index ahead of the closing token
    return i - 1


def build_list_ast(tokens: list[Token]) -> JSONList:
    """
    Builds a JSONList AST.

    Requires:
        - first token is a left bracket [
        - last token is a right bracket ]
    """

    list_value = []
    i = 1
    num_tokens = len(tokens)

    while i < num_tokens - 1:
        token = tokens[i]
        if is_primitive(token):
            list_value.append(build_ast([token]))
            i += 2  # skip comma to the next token
        else:
            closing_index = find_closing_token(tokens, i)
            list_value.append(build_ast(tokens[i : closing_index + 1]))
            i = closing_index + 2  # skip comma to the next token

    return JSONList(list_value)


def build_dict_ast(tokens: list[Token]) -> JSONDict:
    """
    Builds a JSONDict AST.

    Requires:
        - first token is a left parenthesis (
        - last token is a right parenthesis )
    """

    i = 1
    num_tokens = len(tokens)
    fields: dict[str, JSONNode] = {}

    while i < num_tokens - 1:
        start = i

        # make sure key and colon types are correct
        key = tokens[i]
        colon = tokens[i + 1]

        assert key.type == TokenType.STRING
        assert colon.type == TokenType.COLON

        key = build_ast([key])

        # handle primitive values string, number, boolean
        if is_primitive(tokens[i + 2]):
            value = build_ast(tokens[i + 2 : i + 3])
            i = i + 4  # skip key, colon, value, comma
            fields[key] = value
        else:
            # value is another dict or list - find the closing right parenthesis or bracket
            # then parse all the tokens in between into an ast
            start = i + 2
            close_index = find_closing_token(tokens, start)
            value = build_ast(tokens[start : close_index + 1])
            fields[key] = value
            i = close_index + 1

    return JSONDict(fields)


def json_loads(s: str) -> JSON:
    scanner = Scanner(s)
    tokens = scanner.scan_tokens()
    ast = build_ast(tokens)
    j = ast.eval()
    return j
