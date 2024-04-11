from ttoken import Token
from tokentype import TokenType


class ErrorHandler:
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False

    def error(self, token: Token, message: str) -> None:
        if isinstance(token, Token):
            if token.token_type == TokenType.EOF:
                self.report(token.line, "", message)
            else:
                self.report(token.line, "", f" at '{token.lexeme}' {message}")
        else:
            self.report(token, "", message)

    def runtime_error(self, error):
        print(f"{error}\n[line {error.token.line}]")
        self.had_runtime_error = True

    def report(self, line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error{where}: {message}")
        self.had_error = True


class LoxRuntimeError(RuntimeError):
    def __init__(self, token: Token, *args):
        super().__init__(*args)
        self.token = token


class BreakError(Exception):
    pass
