from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Node:
    line: int
    column: int


@dataclass(frozen=True)
class Program(Node):
    statements: list["Stmt"]


class Stmt(Node):
    pass


class Expr(Node):
    pass


@dataclass(frozen=True)
class VarDecl(Stmt):
    name: str
    type_name: str | None
    expr: Expr


@dataclass(frozen=True)
class Assignment(Stmt):
    name: str
    expr: Expr


@dataclass(frozen=True)
class FunctionDecl(Stmt):
    name: str
    params: list[tuple[str, str]]
    return_type: str
    body: list[Stmt]


@dataclass(frozen=True)
class ReturnStmt(Stmt):
    expr: Expr | None


@dataclass(frozen=True)
class IfStmt(Stmt):
    branches: list[tuple[Expr, list[Stmt]]]
    else_body: list[Stmt] | None


@dataclass(frozen=True)
class WhileStmt(Stmt):
    condition: Expr
    body: list[Stmt]


@dataclass(frozen=True)
class ForStmt(Stmt):
    initializer: VarDecl | Assignment
    condition: Expr
    update: Assignment
    body: list[Stmt]


@dataclass(frozen=True)
class InterfaceDecl(Stmt):
    name: str
    fields: list[tuple[str, str]]


@dataclass(frozen=True)
class TypeAliasDecl(Stmt):
    name: str
    target: str


@dataclass(frozen=True)
class ExpressionStmt(Stmt):
    expr: Expr


@dataclass(frozen=True)
class Literal(Expr):
    value: Any


@dataclass(frozen=True)
class Identifier(Expr):
    name: str


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: str
    right: Expr


@dataclass(frozen=True)
class Unary(Expr):
    operator: str
    expr: Expr


@dataclass(frozen=True)
class Call(Expr):
    callee: str
    args: list[Expr]
