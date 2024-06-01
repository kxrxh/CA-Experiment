from logging import log
import logging
from typing import List
from register_file import RegisterFile
from io_controller import IOController
from machine_exceptions import MachineRuntimeError


class DataMemory:
    def __init__(self, data: List[int], register_file: RegisterFile, io_controller: IOController) -> None:
        self.cells = [0, 0] + data
        self.register_file = register_file
        self.io_controller = io_controller

    def read_cell(self, index: int) -> int:
        logging.info(f"Reading cell {index}")
        if index == 0:
            return self.io_controller.read_from_buffer()
        elif index == 1:
            raise MachineRuntimeError("Unable to read from write-only cell")
        return self.cells[index]

    def write_cell(self, index: int, value: int) -> None:
        if index == 0:
            raise MachineRuntimeError("Unable to write to read-only cell")
        elif index == 1:
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
