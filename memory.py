from typing import List
from file_register import RegisterFile
from io_controller import IOController
from machine_exceptions import MachineRuntimeError


class DataMemory:
    register_file: RegisterFile
    io_controller: IOController

    cells: List[int]

    memory_out: int

    def __init__(self, data: List[int], reg_file: RegisterFile, io: IOController) -> None:
        self.cells = [0] + [0] + data
        self.register_file = reg_file
        self.io_controller = io

    def read_cell(self, index: int) -> int:
        if index == 0:
            self.cells[index] = self.io_controller.read_from_buffer()
        elif index == 1:
            raise MachineRuntimeError("unable to read from write-only cell")

        return self.cells[index]

    def write_cell(self, index: int, value: int):
        if index == 0:
            raise MachineRuntimeError("unable to write to read-only cell")
        elif index == 1:
            self.io_controller.write_to_buffer(value)

        self.cells[index] = value

    def latch_write_memory(self):
        self.write_cell(self.register_file.left_out,
                        self.register_file.right_out)

    def latch_read_memory(self):
        self.memory_out = self.read_cell(self.register_file.left_out)


class InstructionMemory:
    cells: List[str]

    def __init__(self, cells: List[str]) -> None:
        self.cells = cells

    def read_cell(self, index: int) -> str:
        return self.cells[index]
