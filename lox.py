import sys
from error import ErrorHandler
from scanner import Scanner
from ttoken import Token
from parser import Parser
from Stmt import Stmt
from interpreter import Interpreter


def main() -> None:
    lox = Lox(error_handler=ErrorHandler())

    if len(sys.argv) > 2:
        print("Usage: pylox [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        lox.run_file(sys.argv[1])
    else:
        lox.run_prompt()


class Lox:
    def __init__(self, error_handler: ErrorHandler):
        self._error_handler = error_handler
        self._source: str = ""
        self._interpreter = Interpreter(self._error_handler)

    def run_file(self, path: str) -> None:
        with open(path, mode="r", encoding=sys.getdefaultencoding()) as f:
            self._source: str = f.read()
            self.run(self._source, self._interpreter.interpret)

        if self._error_handler.had_error:
            sys.exit(65)
        if self._error_handler.had_runtime_error:
            sys.exit(70)

    def run_prompt(self) -> None:
        while (line := input("> ")) not in ["", ".quit"]:
            if not line.endswith(";"):
                line += ";"
            self.run(line, self._interpreter.repl_interpret)
            self._error_handler.had_error = False

    def run(self, source: str, interpret_method) -> None:
        scanner: Scanner = Scanner(source, self._error_handler)
        tokens: list[Token] = scanner.scan_tokens()

        parser: Parser = Parser(tokens, self._error_handler)
        statements: list[Stmt] = parser.parse()

        if self._error_handler.had_error:
            return

        interpret_method(statements)


if __name__ == "__main__":
    main()

