from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import List


class LexError(Exception):
    pass


@dataclass
class Token:
    kind: str
    value: str
    line: int
    column: int


KEYWORDS = {
    "algorithme": "ALGORITHME",
    "debut": "DEBUT",
    "fin": "FIN",
    "tantque": "TANTQUE",
    "faire": "FAIRE",
    "fintantque": "FINTANTQUE",
    "si": "SI",
    "alors": "ALORS",
    "sinon": "SINON",
    "finsi": "FINSI",
    "lire": "LIRE",
    "ecrire": "ECRIRE",
    "mod": "MOD",
    "div": "DIV",
}

SINGLE = {
    "(": "LPAREN",
    ")": "RPAREN",
    ",": "COMMA",
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "/": "SLASH",
}

TWO_CHAR = {
    "<-": "ASSIGN",
    ">=": "GE",
    "<=": "LE",
    "!=": "NE",
}

ONE_OR_TWO = {
    "=": ("EQ", None),
    ">": ("GT", "GE"),
    "<": ("LT", "LE"),
}


def normalize_keyword(word: str) -> str:
    normalized = unicodedata.normalize("NFD", word)
    stripped = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return stripped.lower()


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while not self._is_eof():
            ch = self._peek()
            if ch in " \t\r":
                self._advance()
                continue
            if ch == "\n":
                self._advance_line()
                continue
            if ch == "#":
                self._consume_comment()
                continue
            if ch == '"':
                tokens.append(self._string())
                continue
            if ch.isdigit():
                tokens.append(self._number())
                continue
            if ch.isalpha() or ch == "_" or ch in "éÉàÀèÈùÙçÇâÂêÊîÎôÔûÛ":
                tokens.append(self._identifier_or_keyword())
                continue
            two = self.source[self.pos:self.pos + 2]
            if two in TWO_CHAR:
                tokens.append(self._token(TWO_CHAR[two], two, step=2))
                continue
            if ch in ONE_OR_TWO:
                kind, _ = ONE_OR_TWO[ch]
                tokens.append(self._token(kind, ch, step=1))
                continue
            if ch in SINGLE:
                tokens.append(self._token(SINGLE[ch], ch, step=1))
                continue
            raise LexError(f"Unexpected character '{ch}' at line {self.line}, column {self.col}")
        tokens.append(Token("EOF", "", self.line, self.col))
        return tokens

    def _consume_comment(self) -> None:
        while not self._is_eof() and self._peek() != "\n":
            self._advance()

    def _string(self) -> Token:
        line, col = self.line, self.col
        self._advance()
        chars = []
        while not self._is_eof() and self._peek() != '"':
            if self._peek() == "\n":
                raise LexError(f"Unterminated string at line {line}, column {col}")
            chars.append(self._advance())
        if self._is_eof():
            raise LexError(f"Unterminated string at line {line}, column {col}")
        self._advance()
        return Token("STRING", "".join(chars), line, col)

    def _number(self) -> Token:
        line, col = self.line, self.col
        chars = []
        while not self._is_eof() and self._peek().isdigit():
            chars.append(self._advance())
        if not self._is_eof() and self._peek() == ".":
            chars.append(self._advance())
            if self._is_eof() or not self._peek().isdigit():
                raise LexError(f"Invalid real literal at line {line}, column {col}")
            while not self._is_eof() and self._peek().isdigit():
                chars.append(self._advance())
            return Token("REAL", "".join(chars), line, col)
        return Token("INTEGER", "".join(chars), line, col)

    def _identifier_or_keyword(self) -> Token:
        line, col = self.line, self.col
        chars = []
        while not self._is_eof():
            ch = self._peek()
            if ch.isalnum() or ch == "_" or ch in "éÉàÀèÈùÙçÇâÂêÊîÎôÔûÛ":
                chars.append(self._advance())
            else:
                break
        value = "".join(chars)
        keyword = KEYWORDS.get(normalize_keyword(value))
        if keyword:
            return Token(keyword, value, line, col)
        return Token("IDENT", value, line, col)

    def _token(self, kind: str, value: str, step: int) -> Token:
        t = Token(kind, value, self.line, self.col)
        for _ in range(step):
            self._advance()
        return t

    def _peek(self) -> str:
        return self.source[self.pos]

    def _advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        self.col += 1
        return ch

    def _advance_line(self) -> None:
        self.pos += 1
        self.line += 1
        self.col = 1

    def _is_eof(self) -> bool:
        return self.pos >= len(self.source)
