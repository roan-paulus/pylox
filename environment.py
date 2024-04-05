from ttoken import Token
from error import LoxRuntimeError


# Forward declaration
class Environment:
    pass


class Environment:
    def __init__(self, enclosing: Environment | None = None):
        self._enclosing = enclosing
        self._values: dict[str, object] = {}

    def define(self, name: str, value: object) -> None:
        self._values[name] = value

    def get(self, name: Token) -> object:
        try:
            return self._values[name.lexeme]
        except KeyError:
            if self._enclosing is not None:
                return self._enclosing.get(name)

            LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self._values.keys():
            self._values[name.lexeme] = value
            return

        if self._enclosing is not None:
            self._enclosing.assign(name, value)
            return

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
