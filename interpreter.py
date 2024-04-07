from visitor import StmtVisitor, ExprVisitor
from Stmt import Stmt, ExprStmt, Print, Var, If
from Expr import Expr, Binary, Ternary, Grouping, Literal, Unary, Variable, Assign, Logical
from tokentype import TokenType as TT
from ttoken import Token
from error import ErrorHandler, LoxRuntimeError
from environment import Environment, Unitialized


class Interpreter(StmtVisitor, ExprVisitor):
    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
        self._environment: Environment = Environment()

    def interpret(self, statements: list[Stmt]):
        try:
            for statement in statements:
                self._execute(statement)
        except LoxRuntimeError as error:
            self.error_handler.runtime_error(error)

    def repl_interpret(self, statements: list[Stmt]):
        try:
            for statement in statements:
                if isinstance(statement, ExprStmt):
                    result = self._evaluate(statement.expression)
                    print(self._stringify(result))
                self._execute(statement)
        except LoxRuntimeError as error:
            self.error_handler.runtime_error(error)

    def visit_binary_expr(self, expr: Binary):
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        match expr.operator.token_type:
            case TT.GREATER:
                self._check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            case TT.GREATER_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            case TT.LESS:
                self._check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            case TT.LESS_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            case TT.MINUS:
                self._check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            case TT.BANG_EQUAL:
                return not self._is_equal(left, right)
            case TT.EQUAL_EQUAL:
                return self._is_equal(left, right)
            case TT.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)
                if isinstance(left, str) and isinstance(right, float):
                    if right % 1 > 0:
                        right = str(right)
                    else:
                        right = str(right).split(".")[0]
                    return str(left) + right
                if isinstance(left, float) and isinstance(right, str):
                    if left % 1 > 0:
                        left = str(left)
                    else:
                        left = str(left).split(".")[0]
                    return left + str(right)
                raise LoxRuntimeError(
                    expr.operator, "Operands must be two numbers or two strings."
                )
            case TT.SLASH:
                self._check_number_operands(expr.operator, left, right)
                return float(left) / float(right)
            case TT.STAR:
                self._check_number_operands(expr.operator, left, right)
                return float(left) * float(right)

        # Unreachable.
        return None

    def visit_ternary_expr(self, expr: Ternary):
        if self._evaluate(expr.condition):
            return self._evaluate(expr.left)
        return self._evaluate(expr.right)

    def visit_grouping_expr(self, expr: Grouping):
        return self._evaluate(expr.expression)

    def visit_literal_expr(self, expr: Literal):
        return expr.value

    def visit_logical_expr(self, expr: Logical):
        left: object = self._evaluate(expr.left)

        if expr.operator.token_type == TT.OR:
            if self._is_truthy(left):
                return left
        else:
            if not self._is_truthy(left):
                return left

        return self._evaluate(expr.right)

    def visit_unary_expr(self, expr: Unary):
        right: object = self._evaluate(expr.right)

        match expr.operator.token_type:
            case TT.BANG:
                return not self._is_truthy(right)
            case TT.MINUS:
                self._check_number_operand(expr.operator, right)
                return -float(right)

        # Unreachable.
        return None

    def visit_variable_expr(self, expr: Variable) -> object:
        return self._environment.get(expr.name)

    def _check_number_operand(self, operator: Token, operand: object):
        if isinstance(operand, float):
            return
        raise LoxRuntimeError(operator, "Operand must be a number.")

    def _check_number_operands(self, operator: Token, left: object, right: object):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError(operator, "Operands must be numbers.")

    def _is_truthy(self, obj: object):
        if obj is None:
            return False
        if isinstance(obj, bool):
            return bool(obj)

        return True

    def _is_equal(self, a, b):
        if a is None and b is None:
            return True
        if a == None:
            return False

        return a == b

    def _stringify(self, obj: object) -> str:
        if obj is None:
            return "nil"

        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return text

        return str(obj)

    def _evaluate(self, expr: Expr):
        return expr.accept(self)

    def _execute(self, stmt: Stmt) -> None | Expr:
        stmt.accept(self)

    def _execute_block(self, statements: list[Stmt], environment: Environment):
        prev = self._environment
        try:
            self._environment = environment
            for statement in statements:
                self._execute(statement)
        finally:
            self._environment = prev

    def visit_block_stmt(self, stmt: Stmt) -> None:
        self._execute_block(stmt.statements, Environment(enclosing=self._environment))
        return None

    def visit_exprstmt_stmt(self, stmt: ExprStmt) -> None:
        self._evaluate(stmt.expression)

    def visit_if_stmt(self, stmt: If):
        if self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._execute(stmt.else_branch)

        return None

    def visit_print_stmt(self, stmt: Print) -> None:
        value: object = self._evaluate(stmt.expression)
        print(self._stringify(value))

    def visit_var_stmt(self, stmt: Var) -> None:
        value = Unitialized()
        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)

        self._environment.define(stmt.name.lexeme, value)

    def visit_assign_expr(self, expr: Assign) -> object:
        value: object = self._evaluate(expr.value)
        self._environment.assign(expr.name, value)
        return value
