from typing import List


class TranslatorError(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidArgumentError(TranslatorError):
    def __init__(self, argument: str, expected: List[str]):
        super().__init__(f"Invalid argument '{argument}'. Expected one of {expected}")
