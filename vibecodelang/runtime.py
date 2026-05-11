from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .ast_nodes import (
    Assignment,
    Binary,
    Call,
    Expr,
    ExpressionStmt,
    ForStmt,
    FunctionDecl,
    Identifier,
    IfStmt,
    InterfaceDecl,
    Literal,
    Program,
    ReturnStmt,
    Stmt,
    TypeAliasDecl,
    Unary,
    VarDecl,
    WhileStmt,
)
from .errors import RuntimeVibeError


@dataclass
class Variable:
    type_name: str
    value: Any


class ReturnSignal(Exception):
    def __init__(self, value: Any) -> None:
        self.value = value


class Environment:
    def __init__(self) -> None:
        self.scopes: list[dict[str, Variable]] = [{}]

    def push(self) -> None:
        self.scopes.append({})

    def pop(self) -> None:
        self.scopes.pop()

    def define(self, name: str, type_name: str, value: Any) -> None:
        if name in self.scopes[-1]:
            raise KeyError(f"Variable '{name}' is already defined in this scope")
        self.scopes[-1][name] = Variable(type_name, value)

    def assign(self, name: str, value: Any) -> Variable:
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name].value = value
                return scope[name]
        raise KeyError(f"Undefined variable '{name}'")

    def get(self, name: str) -> Variable:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise KeyError(f"Undefined variable '{name}'")


class Interpreter:
    def __init__(
        self,
        filename: str = "<source>",
        strict_mode: bool = True,
        allow_implicit_types: bool = False,
    ) -> None:
        self.filename = filename
        self.strict_mode = strict_mode
        self.allow_implicit_types = allow_implicit_types
        self.env = Environment()
        self.functions: dict[str, FunctionDecl] = {}
        self.aliases: dict[str, str] = {}
        self.interfaces: dict[str, dict[str, str]] = {}

    def run(self, program: Program) -> None:
        self._register_declarations(program.statements)
        self._execute_block(program.statements, new_scope=False)

    def _register_declarations(self, statements: list[Stmt]) -> None:
        for stmt in statements:
            if isinstance(stmt, FunctionDecl):
                self.functions[stmt.name] = stmt
            elif isinstance(stmt, TypeAliasDecl):
                self.aliases[stmt.name] = stmt.target
            elif isinstance(stmt, InterfaceDecl):
                self.interfaces[stmt.name] = dict(stmt.fields)

    def _execute_block(self, statements: list[Stmt], new_scope: bool = True) -> None:
        if new_scope:
            self.env.push()
        try:
            for stmt in statements:
                self._execute(stmt)
        finally:
            if new_scope:
                self.env.pop()

    def _execute(self, stmt: Stmt) -> None:
        if isinstance(stmt, (FunctionDecl, TypeAliasDecl, InterfaceDecl)):
            return
        if isinstance(stmt, VarDecl):
            value = self._evaluate(stmt.expr)
            type_name = stmt.type_name
            if type_name is None:
                if not self.allow_implicit_types:
                    self._error("Type mismatch", "Variable type is required", stmt)
                type_name = self._infer_type(value)
            self._assert_type(type_name, value, stmt)
            try:
                self.env.define(stmt.name, type_name, value)
            except KeyError as exc:
                self._error("Name error", str(exc), stmt)
        elif isinstance(stmt, Assignment):
            value = self._evaluate(stmt.expr)
            try:
                variable = self.env.get(stmt.name)
            except KeyError as exc:
                self._error("Name error", str(exc), stmt)
            self._assert_type(variable.type_name, value, stmt)
            self.env.assign(stmt.name, value)
        elif isinstance(stmt, ReturnStmt):
            raise ReturnSignal(None if stmt.expr is None else self._evaluate(stmt.expr))
        elif isinstance(stmt, IfStmt):
            for condition, body in stmt.branches:
                if self._truthy(self._evaluate(condition)):
                    self._execute_block(body)
                    return
            if stmt.else_body is not None:
                self._execute_block(stmt.else_body)
        elif isinstance(stmt, WhileStmt):
            while self._truthy(self._evaluate(stmt.condition)):
                self._execute_block(stmt.body)
        elif isinstance(stmt, ForStmt):
            self.env.push()
            try:
                self._execute(stmt.initializer)
                while self._truthy(self._evaluate(stmt.condition)):
                    self._execute_block(stmt.body)
                    self._execute(stmt.update)
            finally:
                self.env.pop()
        elif isinstance(stmt, ExpressionStmt):
            self._evaluate(stmt.expr)
        else:
            self._error("Runtime error", f"Unsupported statement {type(stmt).__name__}", stmt)

    def _evaluate(self, expr: Expr) -> Any:
        if isinstance(expr, Literal):
            if isinstance(expr.value, str):
                return self._interpolate(expr.value, expr)
            return expr.value
        if isinstance(expr, Identifier):
            try:
                return self.env.get(expr.name).value
            except KeyError as exc:
                self._error("Name error", str(exc), expr)
        if isinstance(expr, Unary):
            value = self._evaluate(expr.expr)
            if expr.operator == "-":
                self._require_number(value, expr)
                return -value
            if expr.operator in {"!", "not"}:
                return not self._truthy(value)
        if isinstance(expr, Binary):
            left = self._evaluate(expr.left)
            right = self._evaluate(expr.right)
            return self._apply_binary(expr.operator, left, right, expr)
        if isinstance(expr, Call):
            return self._call(expr)
        self._error("Runtime error", f"Unsupported expression {type(expr).__name__}", expr)

    def _call(self, expr: Call) -> Any:
        args = [self._evaluate(arg) for arg in expr.args]
        if expr.callee == "out":
            if len(args) != 1:
                self._error("Call error", "out expects exactly 1 argument", expr)
            print(args[0])
            return None
        if expr.callee == "outinput":
            if len(args) != 1:
                self._error("Call error", "outinput expects exactly 1 argument", expr)
            return input(str(args[0]))
        if expr.callee not in self.functions:
            self._error("Call error", f"Undefined function '{expr.callee}'", expr)
        function = self.functions[expr.callee]
        if len(args) != len(function.params):
            self._error(
                "Call error",
                f"Function '{function.name}' expects {len(function.params)} argument(s), got {len(args)}",
                expr,
            )
        self.env.push()
        try:
            for (name, type_name), value in zip(function.params, args):
                self._assert_type(type_name, value, expr)
                self.env.define(name, type_name, value)
            try:
                self._execute_block(function.body, new_scope=False)
            except ReturnSignal as signal:
                self._assert_type(function.return_type, signal.value, function)
                return signal.value
            if self._resolve_type(function.return_type) != "void":
                self._error("Return error", f"Function '{function.name}' must return {function.return_type}", function)
            return None
        finally:
            self.env.pop()

    def _apply_binary(self, operator: str, left: Any, right: Any, expr: Expr) -> Any:
        if operator in {"+", "-", "*", "/", "%"}:
            if operator == "+" and (isinstance(left, str) or isinstance(right, str)):
                return str(left) + str(right)
            self._require_number(left, expr)
            self._require_number(right, expr)
            if operator == "+":
                return left + right
            if operator == "-":
                return left - right
            if operator == "*":
                return left * right
            if operator == "/":
                if right == 0:
                    self._error("Math error", "Division by zero", expr)
                return left / right
            if operator == "%":
                return left % right
        if operator in {"==", "!="}:
            return left == right if operator == "==" else left != right
        if operator in {"<", "<=", ">", ">="}:
            if type(left) is not type(right):
                self._error("Type mismatch", "Cannot compare values of different types", expr)
            return {
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[operator]
        if operator == "and":
            return self._truthy(left) and self._truthy(right)
        if operator == "or":
            return self._truthy(left) or self._truthy(right)
        self._error("Runtime error", f"Unknown operator '{operator}'", expr)

    def _interpolate(self, value: str, expr: Expr) -> str:
        def replace(match: re.Match[str]) -> str:
            name = match.group(1).strip()
            try:
                return str(self.env.get(name).value)
            except KeyError as exc:
                self._error("Name error", str(exc), expr)

        return re.sub(r"@\{([^}]+)\}", replace, value)

    def _assert_type(self, expected: str, value: Any, node: Stmt | Expr) -> None:
        resolved = self._resolve_type(expected)
        actual = self._infer_type(value)
        if resolved == "void":
            if value is not None:
                self._type_error(expected, actual, node)
            return
        if resolved != actual:
            self._type_error(expected, actual, node)

    def _resolve_type(self, type_name: str) -> str:
        seen: set[str] = set()
        current = type_name
        while current in self.aliases and current not in seen:
            seen.add(current)
            current = self.aliases[current]
        return current

    def _infer_type(self, value: Any) -> str:
        if value is None:
            return "void"
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return "number"
        if isinstance(value, str):
            return "string"
        return "unknown"

    def _type_error(self, expected: str, actual: str, node: Stmt | Expr) -> None:
        self._error("Type mismatch", f"Expected type '{expected}' but got '{actual}'", node)

    def _require_number(self, value: Any, node: Expr) -> None:
        if self._infer_type(value) != "number":
            self._error("Type mismatch", f"Expected type 'number' but got '{self._infer_type(value)}'", node)

    def _truthy(self, value: Any) -> bool:
        return bool(value)

    def _error(self, title: str, message: str, node: Stmt | Expr) -> None:
        raise RuntimeVibeError(title, message, self.filename, node.line, node.column)
