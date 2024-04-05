from visitor import Visitor
from Expr import Expr, Binary, Ternary, Grouping, Literal, Unary
from ttoken import Token
from tokentype import TokenType


class ASTPrinter(Visitor):
    def print(self, expr: Expr):
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary):
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_ternary_expr(self, expr: Ternary):
        return self._parenthesize(expr.conditional_operator.lexeme + expr.branch_operator.lexeme,
                                  expr.condition, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping):
        return self._parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal):
        if expr.value == None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary):
        return self._parenthesize(expr.operator.lexeme, expr.right)

    def _parenthesize(self, name: str, *exprs: list[Expr]) -> str:
        strings = ["(", name]

        for expr in exprs:
            strings.append(" ")
            strings.append(expr.accept(self))

        strings.append(")")

        return "".join(strings)


class RPNPrinter(Visitor):
    """!!!Doesn't work, falls apart at addition and multiplication followed by a nesting group"""

    def print(self, expr: Expr):
        """Print a type out in polish notation.

        (1 + 2) * (4 - 3) become 1 2 + 4 3 - *
        """
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary):
        return self._RPN(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping):
        return self._RPN("", expr.expression)

    def visit_literal_expr(self, expr: Literal):
        if expr.value == None:
            return "nil"
        return self._RPN(str(expr.value))

    def visit_unary_expr(self, expr: Unary):
        return self._RPN("NEGATE", expr.right)

    def _RPN(self, name: str, *exprs: list[Expr]) -> str:
        strings = []
        after = []
        for expr in exprs:
            # Calls self.visit_<type>_expr
            result = expr.accept(self)
            if isinstance(expr, Literal):
                after.append(result)
            else:
                strings.append(result)

        for string in after:
            strings.append(string)

        # Prevent double spaces when name is empty
        if name != "":
            strings.append(name)

        return " ".join(strings)


# if __name__ == "__main__":
#     expression: Expr = Binary(
#         Grouping(Binary(Literal(1), Token(TokenType.PLUS, "+", None, 1), Literal(2))),
#         Token(TokenType.STAR, "*", None, 1),
#         Grouping(Binary(Literal(4), Token(TokenType.MINUS, "-", None, 1), Literal(3))),
#     )
#     printer = ASTPrinter()
#     printer = RPNPrinter()
#     print(printer.print(expression))
#
