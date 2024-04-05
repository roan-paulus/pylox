from abc import ABC, abstractmethod
from ttoken import Token
from Expr import Expr


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

class Block(Stmt):
    def __init__(self, statements: list[Stmt]):
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)

class ExprStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_exprstmt_stmt(self)

class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_print_stmt(self)

class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_var_stmt(self)
