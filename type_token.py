from enum import Enum
from typing import Self


class TokenType(str, Enum):
    """Enumeration defining types for every possible token."""
    LABEL = 'label'
    REGISTER = 'register'
    NUMBER = 'number'
    INSTRUCTION = 'instruction'
    SECTION = 'section'
    STRING = 'string'


class Token:
    """Class representing a token with its type and value."""

    def __init__(self, type: TokenType, value: str | int):
        self.type = type
        self.value = value

    def __str__(self) -> str:
        return f'{self.type}( {self.value} )'

    def __repr__(self) -> str:
        return str(self)

    def get_type(self) -> TokenType:
        return self.type

    def get_value(self) -> str | int:
        return self.value

    def get_string_value(self) -> str:
        return str(self.value)

    def get_int_value(self) -> int:
        return int(self.value)
