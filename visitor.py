from Expr import *
from abc import ABC, abstractmethod



class ExprVisitor(ABC):
    @abstractmethod
    def visit_assign_expr(self, expr: Assign):
        pass

    @abstractmethod
    def visit_binary_expr(self, expr: Binary):
        pass

    @abstractmethod
    def visit_ternary_expr(self, expr: Ternary):
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping):
        pass

    @abstractmethod
    def visit_literal_expr(self, expr: Literal):
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: Unary):
        pass

    @abstractmethod
    def visit_variable_expr(self, expr: Variable):
        pass

from Stmt import *
from abc import ABC, abstractmethod



class StmtVisitor(ABC):
    @abstractmethod
    def visit_block_stmt(self, stmt: Block):
        pass

    @abstractmethod
    def visit_exprstmt_stmt(self, stmt: ExprStmt):
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt: Print):
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt: Var):
        pass
