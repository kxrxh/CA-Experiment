import logging
from typing import List


class IOController:
    def __init__(self, input_str: str):
        self.input_buffer: List[int] = [ord(char) for char in input_str] + [0]
        self.output_buffer: List[int] = []

    def write_to_buffer(self, value: int) -> None:
        self.output_buffer.append(value)
        logging.debug(f"Adding value to output buffer: {value}")

    def read_from_buffer(self) -> int:
        if self.input_buffer:
            logging.debug(
                f"Reading value from input buffer: {
                          self.input_buffer[0]}"
            )
            return self.input_buffer.pop(0)
        logging.warning("no more values in input buffer to read")
        raise StopIteration("no more values in input buffer")
