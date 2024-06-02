from typing import List


class IOController:
    def __init__(self, input_str: str):
        self.input_buffer: List[int] = [ord(char) for char in input_str] + [0]
        self.output_buffer: List[int] = []

    def write_to_buffer(self, value: int) -> None:
        self.output_buffer.append(value)

    def read_from_buffer(self) -> int:
        if self.input_buffer:
            return self.input_buffer.pop(0)
        raise StopIteration("no more values in input buffer")
