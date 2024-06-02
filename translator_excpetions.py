from typing import List


class TranslatorError(Exception):
    """Base class for translator-related exceptions."""
    pass


class InvalidArgumentError(TranslatorError):
    """Exception raised for invalid arguments passed to a translator."""

    def __init__(self, argument: str, expected: List[str]):
        expected_str = ', '.join(expected)
        super().__init__(f"Invalid argument '{
            argument}'. Expected one of: {expected_str}")
