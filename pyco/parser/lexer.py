from dataclasses import dataclass
from enum import Enum, auto
from re import compile as re_comp
from string import ascii_lowercase, ascii_uppercase
from typing import List, Optional

from .errors import error


class TokenType(Enum):
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    LPAR = auto()
    RPAR = auto()
    LSQB = auto()
    RSQB = auto()
    COLON = auto()
    COMMA = auto()
    SEMI = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    VBAR = auto()
    AMPER = auto()
    LESS = auto()
    GREATER = auto()
    EQUAL = auto()
    DOT = auto()
    PERCENT = auto()
    LBRACE = auto()
    RBRACE = auto()
    EQEQUAL = auto()
    NOTEQUAL = auto()
    LESSEQUAL = auto()
    GREATEREQUAL = auto()
    TILDE = auto()
    CIRCUMFLEX = auto()
    LEFTSHIFT = auto()
    RIGHTSHIFT = auto()
    DOUBLESTAR = auto()
    PLUSEQUAL = auto()
    MINEQUAL = auto()
    STAREQUAL = auto()
    SLASHEQUAL = auto()
    PERCENTEQUAL = auto()
    AMPEREQUAL = auto()
    VBAREQUAL = auto()
    CIRCUMFLEXEQUAL = auto()
    LEFTSHIFTEQUAL = auto()
    RIGHTSHIFTEQUAL = auto()
    DOUBLESTAREQUAL = auto()
    DOUBLESLASH = auto()
    DOUBLESLASHEQUAL = auto()
    AT = auto()
    ATEQUAL = auto()
    ELLIPSIS = auto()
    COLONEQUAL = auto()
    QUOTEQUOTE = auto()
    QUOTE = auto()
    BACKSLASH = auto()


SYMBOLS = {
    "(": TokenType.LPAR,
    ")": TokenType.RPAR,
    "[": TokenType.LSQB,
    "]": TokenType.RSQB,
    ":": TokenType.COLON,
    ",": TokenType.COMMA,
    ";": TokenType.SEMI,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "|": TokenType.VBAR,
    "&": TokenType.AMPER,
    "<": TokenType.LESS,
    ">": TokenType.GREATER,
    "=": TokenType.EQUAL,
    ".": TokenType.DOT,
    "%": TokenType.PERCENT,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "==": TokenType.EQEQUAL,
    "!=": TokenType.NOTEQUAL,
    "<=": TokenType.LESSEQUAL,
    ">=": TokenType.GREATEREQUAL,
    "~": TokenType.TILDE,
    "^": TokenType.CIRCUMFLEX,
    "<<": TokenType.LEFTSHIFT,
    ">>": TokenType.RIGHTSHIFT,
    "**": TokenType.DOUBLESTAR,
    "+=": TokenType.PLUSEQUAL,
    "-=": TokenType.MINEQUAL,
    "*=": TokenType.STAREQUAL,
    "/=": TokenType.SLASHEQUAL,
    "%=": TokenType.PERCENTEQUAL,
    "&=": TokenType.AMPEREQUAL,
    "|=": TokenType.VBAREQUAL,
    "^=": TokenType.CIRCUMFLEXEQUAL,
    "<<=": TokenType.LEFTSHIFTEQUAL,
    ">>=": TokenType.RIGHTSHIFTEQUAL,
    "**=": TokenType.DOUBLESTAREQUAL,
    "//": TokenType.DOUBLESLASH,
    "//=": TokenType.DOUBLESLASHEQUAL,
    "@": TokenType.AT,
    "@=": TokenType.ATEQUAL,
    "...": TokenType.ELLIPSIS,
    ":=": TokenType.COLONEQUAL,
    '"': TokenType.QUOTEQUOTE,
    "'": TokenType.QUOTE,
    "\\": TokenType.BACKSLASH,
}

SYM = "()[]:,;+-*/|&<>=.%{}!~^@'\""
NUM = "0123456789"
IDENT = ascii_lowercase + ascii_uppercase + "_"

IDENT_RE = re_comp(r"^[a-zA-Z_][a-zA-Z0-9_]*")
NUM_RE = re_comp(r"^[0-9]+(\.[0-9]+)?")
STR_DQ_RE = r'"([^"]|\\")*"'
STR_SQ_RE = r"'([^']|\\')*'"
STR_RE = re_comp(fr"^({STR_DQ_RE}|{STR_SQ_RE})")


@dataclass
class Token:
    pos: int
    filename: str
    type: TokenType
    value: Optional[str] = None

    @property
    def format_value(self) -> str:
        return f'"{self.value}"' if self.value else "None"

    def __repr__(self) -> str:
        return f"<Token {self.filename}:{self.pos} type={self.type!r} value={self.format_value}>"


class Lexer:
    """A lexer to tokenise pyco files."""

    def __init__(self, code: str, filename: str) -> None:
        self._code = code
        self._file = filename
        self._line = 0

        self._pos = 0
        self._tokens: List[Token] = []

    @property
    def char(self) -> str:
        return self._code[self._pos]

    def _nchar(self, inc: int = 1) -> Optional[str]:
        if self._pos + inc >= len(self._code):
            return
        return self._code[self._pos + 1]

    def _process_symbol(self) -> Token:
        if self.char in "\"'":
            return self._process_string()

        char = self.char
        if not (nchar := self._nchar()):
            self._pos += 1
            return Token(
                self._line,
                self._file,
                SYMBOLS[char],
            )

        if char + nchar in SYMBOLS:
            if not (nchar2 := self._nchar(2)):
                self._pos += 2
                return Token(
                    self._line,
                    self._file,
                    SYMBOLS[char],
                )

            token = char + nchar + nchar2
            if token not in SYMBOLS:
                self._pos += 2
                return Token(
                    self._line,
                    self._file,
                    SYMBOLS[char + nchar],
                )

            self._pos += 3
            return Token(
                self._line,
                self._file,
                SYMBOLS[token],
            )

        self._pos += 1
        return Token(
            self._line,
            self._file,
            SYMBOLS[char],
        )

    def _process_number(self) -> Token:
        value = NUM_RE.search(self._code[self._pos :])

        assert value, "_process_number failed to find a valid number."

        self._pos += value.end()

        return Token(
            self._line,
            self._file,
            TokenType.NUMBER,
            value.group(),
        )

    def _process_ident(self) -> Token:
        value = IDENT_RE.search(self._code[self._pos :])

        assert value, "_process_ident failed to find a valid identifier."

        self._pos += value.end()

        return Token(
            self._line,
            self._file,
            TokenType.IDENTIFIER,
            value.group(),
        )

    def _process_string(self) -> Token:
        value = STR_RE.search(self._code[self._pos :])

        assert value, "_process_string failed to find a valid identifier."

        self._pos += value.end()

        return Token(
            self._line,
            self._file,
            TokenType.STRING,
            value.group(),
        )

    def next(self) -> Optional[Token]:
        try:
            self.char
        except IndexError:
            return

        if self.char.isspace():
            if self.char == "\n":
                self._line += 1
            self._pos += 1
            return self.next()

        if self.char in SYM:
            return self._process_symbol()

        if self.char in NUM:
            return self._process_number()

        if self.char in IDENT:
            return self._process_ident()

        error(
            self._file,
            self._line,
            "UnexpectedCharacter",
            f"Not expecting to find character: {self.char}",
        )
