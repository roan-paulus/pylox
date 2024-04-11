from ttoken import Token
from Expr import Expr, Variable, Binary, Ternary, Unary, Literal, Grouping, Assign, Logical, Call
from Stmt import Stmt, Var, Print, ExprStmt, Block, If, While, Break, Function
from tokentype import TokenType
from error import ErrorHandler


class Parser:
    def __init__(self, tokens: list[Token], error_handler: ErrorHandler) -> None:
        self._tokens = tokens
        self._current: int = 0
        self._error_handler = error_handler

    def parse(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self._is_at_end():
            try:
                statements.append(self._declaration())
            except ParseError:
                return None

        return statements

    def _comma_expression(self) -> Expr:
        expr: Expr = self._expression()

        while self._match(TokenType.COMMA):
            operator: Token = self._previous()
            right: Expr = self._expression()
            expr = Binary(expr, operator, right)

        return expr

    def _expression(self) -> Expr:
        return self._ternary()

    def _declaration(self):
        try:
            if self._match(TokenType.FUN):
                return self._function("function")
            if self._match(TokenType.VAR):
                return self._var_declaration()
            return self._statement()
        except ParseError:
            self._synchronize()
            return None

    def _statement(self):
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.PRINT):
            return self._print_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.LEFT_BRACE):
            return Block(self._block())
        if self._match(TokenType.BREAK):
            return Break(self._break_statement())

        return self._expression_statement()

    def _for_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer: Stmt
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition: Expr = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment: Expr = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body: Stmt = self._statement()

        if increment is not None:
            body = Block([
                body,
                ExprStmt(increment)
            ])

        if condition is None:
            condition = Literal(True)

        body = While(condition, body)

        if initializer is not None:
            body = Block([
                initializer,
                body,
            ])

        return body

    def _if_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch: Stmt = self._statement()
        else_branch: Stmt | None = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()

        return If(condition, then_branch, else_branch)

    def _print_statement(self):
        value: Expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def _var_declaration(self):
        name: Token = self._consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer: Expr | None = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def _while_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        expr: Expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body: Stmt = self._statement()

        return While(expr, body)

    def _break_statement(self):
        break_keyword = self._previous()
        self._consume(TokenType.SEMICOLON, "Expect ';' after break keyword.")
        return Break(break_keyword)

    def _expression_statement(self):
        value: Expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return ExprStmt(value)

    def _function(self, kind: str) -> Function:
        name: Token = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self._consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters: list[Token] = []

        if not self._check(TokenType.RIGHT_PAREN):
            parameters.append(
                self._consume(TokenType.IDENTIFIER, "Expect parameter name.")
            )
            while self._match(TokenType.COMMA):
                if len(parameters) >= 255:
                    self._error(self._peek(), "Can't have more then 255 parameters.")
                parameters.append(
                    self._consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )

        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        self._consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body: list[Stmt] = self._block()

        return Function(name, parameters, body)

    def _block(self):
        statements: list[Stmt] = []
        while not self._check(TokenType.RIGHT_BRACE):
            statements.append(self._declaration())
        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def _assignment(self):
        expr: Expr = self._or()

        if self._match(TokenType.EQUAL):
            equals: Token = self._previous()
            value: Expr = self._assignment()

            if isinstance(expr, Variable):
                return Assign(expr.name, value)

            self._error(equals, "Invalid assignment target.")

        return expr

    def _or(self) -> Expr:
        expr: Expr = self._and()

        while self._match(TokenType.OR):
            operator: Token = self._previous()
            right: Expr = self._and()
            expr = Logical(expr, operator, right)

        return expr

    def _and(self):
        expr: Expr = self._equality()

        while self._match(TokenType.AND):
            operator: Token = self._previous()
            right: Expr = self._equality()
            expr = Logical(expr, operator, right)

        return expr

    def _ternary(self) -> Expr:
        expr: Expr = self._assignment()

        if not self._match(TokenType.QUESTION_MARK):
            return expr

        operator: Token = self._previous()
        left: Expr = self._expression()

        branch_operator: Token = self._advance()
        if branch_operator.token_type != TokenType.COLON:
            raise self._error(branch_operator, "Expected colon in ternary.")

        right: Expr = self._expression()
        expr = Ternary(expr, operator, left, branch_operator, right)

        return expr

    def _equality(self) -> Expr:
        expr: Expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self._previous()
            right: Expr = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        expr: Expr = self._term()

        while self._match(
            TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL
        ):
            operator: Token = self._previous()
            right: Expr = self._term()
            expr = Binary(expr, operator, right)

        return expr

    def _term(self):
        expr: Expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self._previous()
            right: Expr = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _factor(self):
        expr: Expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self._previous()
            right: Expr = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self):
        if self._match(TokenType.BANG, TokenType.MINUS):
            return Unary(self._previous(), self._unary())
        return self._call()

    def _finish_call(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []

        if not self._check(TokenType.RIGHT_PAREN):
            arguments.append(self._expression())

            while self._match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self._erro(self._peek(), "Can't have more then 255 arguments.")

                arguments.append(self._expression())

        paren: Token = self._consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return Call(callee, paren, arguments)

    def _call(self):
        expr: Expr = self._primary()

        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            else:
                break

        return expr

    def _primary(self):
        if self._match(TokenType.FALSE):
            return Literal(False)
        if self._match(TokenType.TRUE):
            return Literal(True)
        if self._match(TokenType.NIL):
            return Literal(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)

        if self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())

        if self._match(TokenType.LEFT_PAREN):
            expr: Expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise self._error(self._peek(), "Expect expression.")

    def _match(self, *tokentypes: tuple[TokenType]) -> bool:
        for tokentype in tokentypes:
            if self._check(tokentype):
                self._advance()
                return True
        return False

    def _consume(self, tokentype: TokenType, message: str) -> Token:
        if self._check(tokentype):
            return self._advance()
        raise self._error(self._peek(), message)

    def _error(self, token: Token, message: str):
        self._error_handler.error(token, message)
        return ParseError

    def _synchronize(self):
        self._advance()

        while not self._is_at_end():
            if self._previous().token_type == TokenType.SEMICOLON:
                return

            match self._peek().token_type:
                case (TokenType.CLASS
                      | TokenType.FUN
                      | TokenType.VAR
                      | TokenType.FOR
                      | TokenType.IF
                      | TokenType.WHILE
                      | TokenType.PRINT
                      | TokenType.RETURN):
                    return

            self._advance()

    def _check(self, tokentype: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().token_type == tokentype

    def _advance(self) -> Token:
        if not self._is_at_end():
            self._current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().token_type == TokenType.EOF

    def _peek(self) -> Token:
        return self._tokens[self._current]

    def _previous(self) -> Token:
        return self._tokens[self._current - 1]


class ParseError(Exception):
    pass

