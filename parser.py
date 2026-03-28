from enum import Enum
from typing import List, Optional
from dataclasses import dataclass

from pprint import pprint


class TokenType(Enum):
    LEFT_PARENTHESIS = "LEFT_PARENTHESIS"
    RIGHT_PARENTHESIS = "RIGHT_PARENTHESIS"
    STRING = "STRING"
    COLON = "COLON"


@dataclass
class Token:
    type: TokenType
    lexme: str
    literal: Optional[object] = None


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
        elif char == ":":
            self.tokens.append(Token(type=TokenType.COLON, lexme=char))
        elif char == "\n":
            return
        elif char == '"':
            self.scan_string()

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

    def peek(self):
        return self.source[self.current]

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        return self.tokens


if __name__ == "__main__":
    json_path = "./examples/person.json"
    with open(json_path, "r") as f:
        json_str = f.read()

    scanner = Scanner(json_str)
    tokens = scanner.scan_tokens()

    pprint(tokens)
