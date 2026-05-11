from __future__ import annotations

from .errors import LexerError
from .tokens import Token, TokenType

KEYWORDS = {
    "var",
    "function",
    "return",
    "if",
    "elseif",
    "else",
    "for",
    "while",
    "interface",
    "type",
    "true",
    "false",
    "and",
    "or",
    "not",
}

TWO_CHAR_SYMBOLS = {"==", "!=", "<=", ">="}
ONE_CHAR_SYMBOLS = set("[]{}():,;+-*/%<>=!")


class Lexer:
    def __init__(self, source: str, filename: str = "<source>") -> None:
        self.source = source
        self.filename = filename
        self.index = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while not self._at_end():
            char = self._peek()
            if char in " \t\r":
                self._advance()
            elif char == "\n":
                self._advance_line()
            elif char == "/" and self._peek_next() == "/":
                self._skip_line_comment()
            elif char == "!" and self._peek_next() == "!":
                self._skip_bang_comment()
            elif char.isalpha() or char == "_":
                tokens.append(self._identifier())
            elif char.isdigit():
                tokens.append(self._number())
            elif char == '"':
                tokens.append(self._string())
            else:
                tokens.append(self._symbol())
        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens

    def _identifier(self) -> Token:
        line, column = self.line, self.column
        start = self.index
        while not self._at_end() and (self._peek().isalnum() or self._peek() == "_"):
            self._advance()
        value = self.source[start : self.index]
        kind = TokenType.KEYWORD if value in KEYWORDS else TokenType.IDENT
        return Token(kind, value, line, column)

    def _number(self) -> Token:
        line, column = self.line, self.column
        start = self.index
        while not self._at_end() and self._peek().isdigit():
            self._advance()
        if not self._at_end() and self._peek() == ".":
            self._advance()
            while not self._at_end() and self._peek().isdigit():
                self._advance()
        return Token(TokenType.NUMBER, self.source[start : self.index], line, column)

    def _string(self) -> Token:
        line, column = self.line, self.column
        self._advance()
        chars: list[str] = []
        while not self._at_end() and self._peek() != '"':
            char = self._advance()
            if char == "\\" and not self._at_end():
                escaped = self._advance()
                chars.append({"n": "\n", "t": "\t", '"': '"'}.get(escaped, escaped))
            else:
                chars.append(char)
        if self._at_end():
            raise LexerError("Unterminated string literal", self.filename, line, column)
        self._advance()
        return Token(TokenType.STRING, "".join(chars), line, column)

    def _symbol(self) -> Token:
        line, column = self.line, self.column
        two = self.source[self.index : self.index + 2]
        if two in TWO_CHAR_SYMBOLS:
            self._advance()
            self._advance()
            return Token(TokenType.SYMBOL, two, line, column)
        char = self._advance()
        if char in ONE_CHAR_SYMBOLS:
            return Token(TokenType.SYMBOL, char, line, column)
        raise LexerError(f"Unexpected character '{char}'", self.filename, line, column)

    def _skip_line_comment(self) -> None:
        while not self._at_end() and self._peek() != "\n":
            self._advance()

    def _skip_bang_comment(self) -> None:
        self._advance()
        self._advance()
        if not self._at_end() and self._peek() == "*":
            self._advance()
            self._skip_block_comment()
            return
        self._skip_line_comment()

    def _skip_block_comment(self) -> None:
        start_line, start_column = self.line, self.column - 3
        while not self._at_end():
            if self._peek() == "*" and self._peek_next() == "!" and self._peek_after_next() == "!":
                self._advance()
                self._advance()
                self._advance()
                return
            if self._peek() == "\n":
                self._advance_line()
            else:
                self._advance()
        raise LexerError("Unterminated block comment", self.filename, start_line, start_column)

    def _peek(self) -> str:
        return self.source[self.index]

    def _peek_next(self) -> str:
        if self.index + 1 >= len(self.source):
            return "\0"
        return self.source[self.index + 1]

    def _peek_after_next(self) -> str:
        if self.index + 2 >= len(self.source):
            return "\0"
        return self.source[self.index + 2]

    def _advance(self) -> str:
        char = self.source[self.index]
        self.index += 1
        self.column += 1
        return char

    def _advance_line(self) -> None:
        self.index += 1
        self.line += 1
        self.column = 1

    def _at_end(self) -> bool:
        return self.index >= len(self.source)
