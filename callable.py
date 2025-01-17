from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import time

from Stmt import Function
from lox_return import LoxReturn
from environment import Environment


if TYPE_CHECKING:
    from interpreter import Interpreter


class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        pass

    @abstractmethod
    def arity(self) -> int:
        pass


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment) -> None:
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        environment: Environment = Environment(self.closure)

        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])

        try:
            interpreter._execute_block(self.declaration.body, environment)
        except LoxReturn as r:
            return r.value

        return None

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"


class LoxClock(LoxCallable):
    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        return time.time()

    def arity(self) -> int:
        return 0

    def __str__(self) -> str:
        return "<native fn>"

