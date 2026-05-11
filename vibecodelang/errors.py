from __future__ import annotations


class VibeCodeError(Exception):
    """Base error with source location context."""

    def __init__(
        self,
        title: str,
        message: str,
        filename: str = "<source>",
        line: int | None = None,
        column: int | None = None,
    ) -> None:
        self.title = title
        self.message = message
        self.filename = filename
        self.line = line
        self.column = column
        super().__init__(self.format())

    def format(self) -> str:
        parts = [f"VibeCodeError: {self.title}", "", f"File: {self.filename}"]
        if self.line is not None:
            parts.append(f"Line: {self.line}")
        if self.column is not None:
            parts.append(f"Column: {self.column}")
        parts.extend(["", self.message])
        return "\n".join(parts)


class LexerError(VibeCodeError):
    def __init__(self, message: str, filename: str, line: int, column: int) -> None:
        super().__init__("Lexing failed", message, filename, line, column)


class ParseError(VibeCodeError):
    def __init__(self, message: str, filename: str, line: int, column: int) -> None:
        super().__init__("Parse failed", message, filename, line, column)


class RuntimeVibeError(VibeCodeError):
    pass
