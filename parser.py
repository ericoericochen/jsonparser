from enum import Enum
from typing import List, Optional, Dict
from dataclasses import dataclass
from pprint import pprint
from abc import ABC, abstractmethod


JSON = Dict | List | str | int | float | bool

# Tokens


class TokenType(Enum):
    # symbols
    LEFT_PARENTHESIS = "LEFT_PARENTHESIS"
    RIGHT_PARENTHESIS = "RIGHT_PARENTHESIS"
    COLON = "COLON"

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
        elif char == ":":
            self.tokens.append(Token(type=TokenType.COLON, lexme=char))
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
        while is_digit(self.peek()):
            self.advance()

        if self.peek() == "." and is_digit(self.peek(1)):
            self.advance()
            while is_digit(self.peek()):
                self.advance()

        lexme = self.get_lexme()

        if "." in lexme:
            literal = float(lexme)
        else:
            literal = int(lexme)

        self.tokens.append(Token(type=TokenType.NUMBER, lexme=lexme, literal=literal))

    def scan_boolean(self):
        print("scanning boolean yo")
        while is_lowercase_alpha(self.peek()):
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
    fields: dict[JSONString, JSONNode]

    def eval(self) -> JSON:
        return {k.eval(): v.eval() for k, v in self.fields.items()}


def is_primitive(token: Token):
    return token.type in {TokenType.STRING, TokenType.NUMBER}


def build_ast(tokens: list[Token]) -> JSONNode:
    # print("building ast")
    # pprint(tokens)

    # base case: primitives string, number, boolean
    if len(tokens) == 1:
        token = tokens[0]

        if token.type == TokenType.STRING:
            return JSONString(value=token.literal)
        elif token.type == TokenType.NUMBER:
            return JSONNumber(value=token.literal)
        elif token.type == TokenType.BOOLEAN:
            return JSONBoolean(value=token.literal)

    # parse json dict or list
    if len(tokens) >= 2:
        first_token = tokens[0]
        last_token = tokens[-1]

        if (
            first_token.type == TokenType.LEFT_PARENTHESIS
            and last_token.type == TokenType.RIGHT_PARENTHESIS
        ):
            return build_dict_ast(tokens)


def build_dict_ast(tokens: list[Token]) -> JSONDict:
    """
    Builds a JSONDict AST.

    Requires first token to be a left parenthesis and last token to be a right parenthesis.
    """

    i = 1
    num_tokens = len(tokens)
    fields: dict[str, JSONNode] = {}

    while i < num_tokens - 1:
        # make sure key and colon types are correct
        key = tokens[i]
        colon = tokens[i + 1]

        assert key.type == TokenType.STRING
        assert colon.type == TokenType.COLON

        key = build_ast([key])

        # parse value into JSONNode
        value_tokens = [tokens[i + 2]]

        # handle primitive values string, number, boolean
        if value_tokens[0].type == TokenType.STRING:
            value = build_ast(value_tokens)
            i = i + 3  # advance to next key
        elif value_tokens[0].type == TokenType.NUMBER:
            value = build_ast(value_tokens)
            i = i + 3
        elif value_tokens[0].type == TokenType.BOOLEAN:
            value = build_ast(value_tokens)
            i = i + 3

        fields[key] = value

    return JSONDict(fields=fields)


def parse(tokens: List[Token]) -> JSON:
    print("parsing tokens into json")

    pprint(tokens)
