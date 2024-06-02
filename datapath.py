from __future__ import annotations

import logging

from alu import Alu
from io_controller import IOController
from machine_exceptions import InvalidMuxSignalError
from memory import DataMemory, InstructionMemory
from microcode import Signal
from register_file import RegisterFile


class DataPath:
    data_memory: DataMemory
    instruction_memory: InstructionMemory
    register_file: RegisterFile
    alu: Alu

    io_controller: IOController
    pc_mux: Signal
    pc: int

    data_src_mux: Signal

    cu_address_out: int
    cu_data_out: int

    def __init__(self, instructions: list[str], data: list[int], input_stream: str):
        self.pc = 0

        self.register_file = RegisterFile()
        # Connect ALU to register file
        self.alu = Alu(self.register_file)

        self.io_controller = IOController(input_stream)
        # Connect Datamemory to register file and io controller
        self.data_memory = DataMemory(data, self.register_file, self.io_controller)

        self.instruction_memory = InstructionMemory(instructions)

        self.cu_address_out = 0
        self.cu_data_out = 0
        self.data_src = 0
        self.pc_mux = Signal.SEL_PC_INC

    def sel_pc(self, value: Signal):
        self.pc_mux = value

    def latch_pc(self):
        match self.pc_mux:
            case Signal.SEL_PC_ADDR:
                self.pc = self.cu_address_out
            case Signal.SEL_PC_INC:
                self.pc += 1
            case _:
                logging.error(f"invalid pc mux signal:  {self.pc_mux}")
                raise InvalidMuxSignalError("pc_mux")

    def sel_data_src(self, value: Signal):
        self.data_src_mux = value

    def get_register_file_input(self) -> int:
        match self.data_src_mux:
            case Signal.SEL_SRC_MEM:
                return self.data_memory.memory_out
            case Signal.SEL_SRC_ALU:
                return self.alu.alu_result
            case Signal.SEL_SRC_CU:
                return self.cu_data_out
            case _:
                logging.error(
                    f"invalid signal for data source mux:  {
                              self.data_src_mux}"
                )
                raise InvalidMuxSignalError("data_src_mux")
