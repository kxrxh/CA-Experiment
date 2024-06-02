from logging import log
import logging
from typing import List
from register_file import RegisterFile
from io_controller import IOController
from machine_exceptions import MachineRuntimeError

MAX_MEMORY_SIZE = 65535


class DataMemory:
    def __init__(self, data: List[int], register_file: RegisterFile, io_controller: IOController) -> None:
        # Initialize all cells with 0
        self.cells = [0] * MAX_MEMORY_SIZE

        initial_data = [0, 0] + data
        # Truncate initial_data if it exceeds MAX_MEMORY_SIZE
        if len(initial_data) > MAX_MEMORY_SIZE:
            initial_data = initial_data[:MAX_MEMORY_SIZE]

        # Set initial values for the first few cells
        self.cells[: len(initial_data)] = initial_data
        self.register_file = register_file
        self.io_controller = io_controller

    def read_cell(self, index: int) -> int:
        if index == 0:
            logging.debug("Reading from 'in' buffer")
            return self.io_controller.read_from_buffer()
        elif index == 1:
            logging.error("Unable to read from write-only cell")
            raise MachineRuntimeError("Unable to read from write-only cell")
        return self.cells[index]

    def write_cell(self, index: int, value: int) -> None:
        if index == 0:
            logging.error("Unable to write to read-only cell")
            raise MachineRuntimeError("Unable to write to read-only cell")
        elif index == 1:
            logging.debug("Writing to 'out' buffer")
            self.io_controller.write_to_buffer(value)
        self.cells[index] = value

    def latch_write_memory(self) -> None:
        left_out = self.register_file.left_out
        right_out = self.register_file.right_out
        self.write_cell(left_out, right_out)

    def latch_read_memory(self) -> None:
        left_out = self.register_file.left_out
        self.memory_out = self.read_cell(left_out)


class InstructionMemory:
    def __init__(self, cells: List[str]) -> None:
        self.cells = cells

    def read_cell(self, index: int) -> str:
        return self.cells[index - 1]
