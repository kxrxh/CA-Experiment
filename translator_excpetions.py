from __future__ import annotations


class TranslatorError(Exception):
    """Base class for translator-related exceptions."""
    pass


class InvalidArgumentCountError(TranslatorError):
    def __init__(self, expected: list[int]):
        super().__init__("Invalid argument count: expected {expected}")


class NoTokenError(TranslatorError):
    def __init__(self):
        super().__init__("No token were provided")


class InvalidArgumentError(TranslatorError):
    """Exception raised for invalid arguments passed to a translator."""

    def __init__(self, argument: str, expected: list[str]):
        expected_str = ", ".join(expected)
        super().__init__(f"Invalid argument '{
            argument}'. Expected one of: {expected_str}")
