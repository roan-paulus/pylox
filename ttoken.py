from tokentype import TokenType


class Token:
    def __init__(self, token_type, lexeme, literal, line):
        self.token_type: TokenType = token_type
        self.lexeme: str = lexeme
        self.literal: object = literal
        self.line: int = line

    def __str__(self):
        return f"{self.token_type} {self.lexeme} {self.literal}"

