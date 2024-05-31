from typing import List


class IOController:
    input_buffer: List[int]
    output_buffer: List[int]

    def __init__(self, input: str):
        self.input_buffer = list(map(ord, list(input)))  # str to int array
        self.output_buffer: List[int] = []

    def write_to_buffer(self, value: int):
        self.output_buffer.append(value)

    def read_from_buffer(self) -> int:
        return self.output_buffer.pop(0)
