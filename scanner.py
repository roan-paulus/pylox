from pdb import set_trace

from ttoken import Token
from ttoken import TokenType
from error import ErrorHandler


class Scanner:
    def __init__(self, source: str, error_handler: ErrorHandler):
        self._source: str = source
        self._tokens: list[Token] = []
        self._error_handler: ErrorHandler = error_handler

        self._start: int = 0
        self._current: int = 0
        self._line: int = 1

        self._keywords = {
            "and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "this": TokenType.THIS,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE,
            "break": TokenType.BREAK,
        }

    def scan_tokens(self):
        while not self.is_at_end():
            # We are at the beginning of the next lexeme.
            self._start = self._current
            self.scan_token()

        self._tokens.append(Token(TokenType.EOF, "", None, self._line))
        return self._tokens

    def scan_token(self) -> None:
        char: str = self.advance()
        TT = TokenType
        match char:
            case "(":
                self.add_token(TT.LEFT_PAREN)
            case ")":
                self.add_token(TT.RIGHT_PAREN)
            case "{":
                self.add_token(TT.LEFT_BRACE)
            case "}":
                self.add_token(TT.RIGHT_BRACE)
            case ",":
                self.add_token(TT.COMMA)
            case ".":
                self.add_token(TT.DOT)
            case ":":
                self.add_token(TT.COLON)
            case "?":
                self.add_token(TT.QUESTION_MARK)
            case "-":
                self.add_token(TT.MINUS)
            case "+":
                self.add_token(TT.PLUS)
            case ";":
                self.add_token(TT.SEMICOLON)
            case "*":
                self.add_token(TT.STAR)
            case "!":
                self.add_token(TT.BANG_EQUAL if self.match("=") else TT.BANG_EQUAL)
            case "=":
                self.add_token(TT.EQUAL_EQUAL if self.match("=") else TT.EQUAL)
            case "<":
                self.add_token(TT.LESS_EQUAL if self.match("=") else TT.LESS)
            case ">":
                self.add_token(TT.GREATER_EQUAL if self.match("=") else TT.GREATER)
            case "/":
                if self.match("/"):
                    while self.peek() != "\n" and not self.is_at_end():
                        self.advance()
                elif self.match("*"):
                    self.block_comment()
                else:
                    self.add_token(TT.SLASH)
            case " " | "\r" | "\t":
                pass
            case "\n":
                self._line += 1
            case '"':
                self.string()
            case _:
                if char.isdigit():
                    self.number()
                elif self.is_alpha_numeric(char):
                    self.identifier()
                else:
                    self._error_handler.error(self._line, "Unexpected character.")

    def add_token(self, token_type: TokenType, literal: object | None = None) -> None:
        text = self._source[self._start:self._current]
        self._tokens.append(Token(token_type, text, literal, self._line))

    def identifier(self) -> None:
        while self.is_alpha_numeric(self.peek()):
            self.advance()

        text = self._source[self._start:self._current]
        if text in self._keywords.keys():
            self.add_token(self._keywords[text])
        else:
            self.add_token(TokenType.IDENTIFIER)

    def advance(self) -> str:
        self._current += 1
        return self._source[self._current - 1]

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self._source[self._current]

    def peek_next(self) -> str:
        next = self._current + 1
        if next >= len(self._source):
            return "\0"
        return self._source[next]

    def is_alpha(self, c: str) -> bool:
        o = ord(c)
        return ord("a") <= o <= ord("z") or ord("A") <= o <= ord("Z") or c == "_"

    def is_alpha_numeric(self, c: str) -> bool:
        return self.is_alpha(c) or c.isdigit()

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self._source[self._current] != expected:
            return False

        self._current += 1
        return True

    def string(self) -> None:
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self._line += 1
            self.advance()

        if self.is_at_end():
            self._error_handler.error(self._line, "Unterminated string.")
            return

        # The closing ".
        self.advance()

        value: str = self._source[self._start + 1:self._current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self) -> None:
        while self.peek().isdigit():
            self.advance()

        # Look for a fractional part.
        if self.peek() == "." and self.peek_next().isdigit():
            # Consume the "."
            self.advance()
            while self.peek().isdigit():
                self.advance()

        self.add_token(TokenType.NUMBER, float(self._source[self._start:self._current]))

    def block_comment(self):
        while not self.is_at_end():
            char = self.advance()
            # End of a code block
            if char == "*" and self.peek() == "/":
                self.advance()
                break
            # Start of new code block
            if char == "/" and self.peek() == "*":
                self.advance()
                self.block_comment()

    def is_at_end(self) -> bool:
        return self._current >= len(self._source)

