from typing import List
from alu import Alu
from control_unit import ControlUnit
from file_register import RegisterFile
from io_controller import IOController
from machine_exceptions import MachineRuntimeError
from memory import DataMemory, InstructionMemory
from microcode_new import Signal


class DataPath:
    data_memory: DataMemory
    instruction_memory: InstructionMemory
    register_file: RegisterFile
    alu: Alu

    control_unit: ControlUnit
    io_controller: IOController

    pc_mux: Signal
    pc: int

    data_src_mux: Signal

    def __init__(self, instructions: List[str], data: List[int], input: str):
        self.pc = 0

        self.register_file = RegisterFile()
        # Connect ALU to register file
        self.alu = Alu(self.register_file)
        # Connect control unit to register file and dapath
        self.control_unit = ControlUnit(self.alu, self)

        self.io_controller = IOController(input)
        # Connect Datamemory to register file and io controller
        self.data_memory = DataMemory(
            data, self.register_file, self.io_controller)

        self.instruction_memory = InstructionMemory(instructions)

    def sel_pc(self, value: Signal):
        self.pc_mux = value

    def latch_pc(self):
        match self.pc_mux:
            case Signal.SEL_PC_ADDR:
                self.pc = self.control_unit.address_out
            case Signal.SEL_PC_INC:
                self.pc += 1
            case _:
                raise MachineRuntimeError(f"invalid mux value  {self.pc_mux}")

    def sel_data_src(self, value: Signal):
        self.data_src_mux = value

    def get_register_file_input(self) -> int:
        match self.data_src_mux:
            case Signal.SEL_SRC_MEM:
                return self.data_memory.memory_out
            case Signal.SEL_SRC_ALU:
                return self.alu.alu_result
            case Signal.SEL_SRC_CU:
                return self.control_unit.data_out
            case _:
                raise MachineRuntimeError(
                    f"invalid signal for data source mux:  {self.data_src_mux}")