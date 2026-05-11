from __future__ import annotations

from .lexer import Lexer
from .parser import Parser
from .runtime import Interpreter


def interpret_source(
    source: str,
    filename: str = "<source>",
    strict_mode: bool = True,
    allow_implicit_types: bool = False,
) -> None:
    tokens = Lexer(source, filename).tokenize()
    program = Parser(tokens, filename).parse()
    Interpreter(filename, strict_mode, allow_implicit_types).run(program)
