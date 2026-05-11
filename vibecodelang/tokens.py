from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    IDENT = auto()
    NUMBER = auto()
    STRING = auto()
    KEYWORD = auto()
    SYMBOL = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    kind: TokenType
    value: str
    line: int
    column: int
