from __future__ import annotations

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
from .errors import ParseError
from .tokens import Token, TokenType

PRECEDENCE = {
    "or": 1,
    "and": 2,
    "==": 3,
    "!=": 3,
    "<": 4,
    "<=": 4,
    ">": 4,
    ">=": 4,
    "+": 5,
    "-": 5,
    "*": 6,
    "/": 6,
    "%": 6,
}


class Parser:
    def __init__(self, tokens: list[Token], filename: str = "<source>") -> None:
        self.tokens = tokens
        self.filename = filename
        self.current = 0

    def parse(self) -> Program:
        statements: list[Stmt] = []
        while not self._check_kind(TokenType.EOF):
            statements.append(self._statement())
        first = self.tokens[0]
        return Program(first.line, first.column, statements)

    def _statement(self) -> Stmt:
        if self._match_keyword("var"):
            return self._var_decl(require_var_keyword=False)
        if self._match_keyword("function"):
            return self._function_decl()
        if self._match_keyword("return"):
            token = self._previous()
            if self._check("}"):
                return ReturnStmt(token.line, token.column, None)
            return ReturnStmt(token.line, token.column, self._expression())
        if self._match_keyword("if"):
            return self._if_stmt()
        if self._match_keyword("while"):
            return self._while_stmt()
        if self._match_keyword("for"):
            return self._for_stmt()
        if self._match_keyword("interface"):
            return self._interface_decl()
        if self._match_keyword("type"):
            return self._type_alias()
        if self._check_kind(TokenType.IDENT) and self._peek_next().value == "=":
            return self._assignment()
        expr = self._expression()
        return ExpressionStmt(expr.line, expr.column, expr)

    def _var_decl(self, require_var_keyword: bool = True) -> VarDecl:
        name = self._consume_kind(TokenType.IDENT, "Expected variable name")
        type_name: str | None = None
        if self._match(":"):
            type_name = self._consume_type_name("Expected type name").value
        elif require_var_keyword:
            self._error_here("Expected ':' and variable type")
        self._consume_any({">", "="}, "Expected '>' before variable value")
        expr = self._expression()
        return VarDecl(name.line, name.column, name.value, type_name, expr)

    def _assignment(self) -> Assignment:
        name = self._consume_kind(TokenType.IDENT, "Expected variable name")
        self._consume("=", "Expected '=' in assignment")
        expr = self._expression()
        return Assignment(name.line, name.column, name.value, expr)

    def _function_decl(self) -> FunctionDecl:
        name = self._consume_kind(TokenType.IDENT, "Expected function name")
        self._consume("[", "Expected '[' before function parameters")
        params: list[tuple[str, str]] = []
        if not self._check("]"):
            while True:
                param = self._consume_kind(TokenType.IDENT, "Expected parameter name")
                self._consume(":", "Expected ':' after parameter name")
                param_type = self._consume_type_name("Expected parameter type")
                params.append((param.value, param_type.value))
                if not self._match(","):
                    break
        self._consume("]", "Expected ']' after parameters")
        self._consume(">", "Expected '>' before function return type")
        return_type = self._consume_type_name("Expected function return type")
        body = self._block()
        return FunctionDecl(name.line, name.column, name.value, params, return_type.value, body)

    def _if_stmt(self) -> IfStmt:
        token = self._previous()
        branches = [(self._bracketed_expression(), self._block())]
        while self._match_keyword("elseif"):
            branches.append((self._bracketed_expression(), self._block()))
        else_body = self._block() if self._match_keyword("else") else None
        return IfStmt(token.line, token.column, branches, else_body)

    def _while_stmt(self) -> WhileStmt:
        token = self._previous()
        condition = self._bracketed_expression()
        return WhileStmt(token.line, token.column, condition, self._block())

    def _for_stmt(self) -> ForStmt:
        token = self._previous()
        self._consume("[", "Expected '[' after for")
        initializer: VarDecl | Assignment
        if self._check_kind(TokenType.IDENT) and self._peek_next().value == ":":
            initializer = self._var_decl(require_var_keyword=False)
        else:
            initializer = self._assignment()
        self._consume(";", "Expected ';' after for initializer")
        condition = self._expression()
        self._consume(";", "Expected ';' after for condition")
        update = self._assignment()
        self._consume("]", "Expected ']' after for update")
        return ForStmt(token.line, token.column, initializer, condition, update, self._block())

    def _interface_decl(self) -> InterfaceDecl:
        token = self._previous()
        self._consume(">", "Expected '>' after interface")
        name = self._consume_kind(TokenType.IDENT, "Expected interface name")
        self._consume("[", "Expected '[' before interface fields")
        fields: list[tuple[str, str]] = []
        while not self._check("]"):
            field = self._consume_kind(TokenType.IDENT, "Expected interface field name")
            self._consume(":", "Expected ':' after field name")
            field_type = self._consume_type_name("Expected field type")
            fields.append((field.value, field_type.value))
        self._consume("]", "Expected ']' after interface fields")
        return InterfaceDecl(token.line, token.column, name.value, fields)

    def _type_alias(self) -> TypeAliasDecl:
        token = self._previous()
        name = self._consume_kind(TokenType.IDENT, "Expected type alias name")
        self._consume(">", "Expected '>' after type alias name")
        target = self._consume_type_name("Expected target type")
        return TypeAliasDecl(token.line, token.column, name.value, target.value)

    def _block(self) -> list[Stmt]:
        self._consume("{", "Expected '{' before block")
        body: list[Stmt] = []
        while not self._check("}") and not self._check_kind(TokenType.EOF):
            body.append(self._statement())
        self._consume("}", "Expected '}' after block")
        return body

    def _bracketed_expression(self) -> Expr:
        self._consume("[", "Expected '[' before condition")
        expr = self._expression()
        self._consume("]", "Expected ']' after condition")
        return expr

    def _expression(self, min_precedence: int = 1) -> Expr:
        expr = self._unary()
        while self._operator_precedence() >= min_precedence:
            operator = self._advance()
            right = self._expression(PRECEDENCE[operator.value] + 1)
            expr = Binary(operator.line, operator.column, expr, operator.value, right)
        return expr

    def _unary(self) -> Expr:
        if self._match_any({"!", "-", "not"}):
            operator = self._previous()
            return Unary(operator.line, operator.column, operator.value, self._unary())
        return self._primary()

    def _primary(self) -> Expr:
        token = self._advance()
        if token.kind == TokenType.NUMBER:
            value = float(token.value) if "." in token.value else int(token.value)
            return Literal(token.line, token.column, value)
        if token.kind == TokenType.STRING:
            return Literal(token.line, token.column, token.value)
        if token.kind == TokenType.KEYWORD and token.value in {"true", "false"}:
            return Literal(token.line, token.column, token.value == "true")
        if token.kind == TokenType.IDENT:
            if self._match("("):
                args: list[Expr] = []
                if not self._check(")"):
                    while True:
                        args.append(self._expression())
                        if not self._match(","):
                            break
                self._consume(")", "Expected ')' after arguments")
                return Call(token.line, token.column, token.value, args)
            return Identifier(token.line, token.column, token.value)
        if token.value == "(":
            expr = self._expression()
            self._consume(")", "Expected ')' after expression")
            return expr
        raise ParseError(f"Expected expression, got '{token.value}'", self.filename, token.line, token.column)

    def _operator_precedence(self) -> int:
        token = self._peek()
        if token.value in PRECEDENCE:
            return PRECEDENCE[token.value]
        return 0

    def _match_keyword(self, value: str) -> bool:
        return self._match_token(TokenType.KEYWORD, value)

    def _match(self, value: str) -> bool:
        return self._match_token(TokenType.SYMBOL, value)

    def _match_any(self, values: set[str]) -> bool:
        if self._peek().value in values:
            self._advance()
            return True
        return False

    def _match_token(self, kind: TokenType, value: str) -> bool:
        if self._peek().kind == kind and self._peek().value == value:
            self._advance()
            return True
        return False

    def _consume(self, value: str, message: str) -> Token:
        if self._check(value):
            return self._advance()
        self._error_here(message)

    def _consume_any(self, values: set[str], message: str) -> Token:
        if self._peek().value in values:
            return self._advance()
        self._error_here(message)

    def _consume_kind(self, kind: TokenType, message: str) -> Token:
        if self._check_kind(kind):
            return self._advance()
        self._error_here(message)

    def _consume_type_name(self, message: str) -> Token:
        if self._check_kind(TokenType.IDENT) or (
            self._check_kind(TokenType.KEYWORD) and self._peek().value not in {"if", "else", "for", "while"}
        ):
            return self._advance()
        self._error_here(message)

    def _check(self, value: str) -> bool:
        return self._peek().value == value

    def _check_kind(self, kind: TokenType) -> bool:
        return self._peek().kind == kind

    def _advance(self) -> Token:
        token = self._peek()
        if not self._check_kind(TokenType.EOF):
            self.current += 1
        return token

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _peek_next(self) -> Token:
        if self.current + 1 >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.current + 1]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _error_here(self, message: str) -> None:
        token = self._peek()
        raise ParseError(message, self.filename, token.line, token.column)
