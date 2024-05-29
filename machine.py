from enum import Enum
import logging
import sys
from typing import List

from machine_error import InvalidRegisterIndex, MachineRuntimeError
from microcode import AluOperation, Mux


class RegisterFile:
    r0: int  # Zero register (Always 0)
    r1: int
    r2: int
    r3: int
    r4: int
    r5: int
    r6: int
    r7: int
    r8: int
    r9: int
    r10: int
    rd: int
    rip: int
    rpc: int

    mux_left_out: Mux
    mux_right_out: Mux

    def __init__(self):
        self.r0 = 0
        self.r1 = 0
        self.r2 = 0
        self.r3 = 0
        self.r4 = 0
        self.r5 = 0
        self.r6 = 0
        self.r7 = 0
        self.r8 = 0
        self.r9 = 0
        self.r10 = 0
        self.r11 = 0
        self.r12 = 0
        self.r13 = 0
        self.r14 = 0
        self.r15 = 0

    def latch_reg_n(self, index: int, value: int) -> None:
        if index == 0:
            raise InvalidRegisterIndex("register with index 0 is immutable")
        elif 1 <= index <= 15:
            setattr(self, f"r{index}", value)
        else:
            raise InvalidRegisterIndex(f"register r{index} does not exist")

    def sel_left_reg(self, signal: Mux):
        if int(Mux.SEL_R0) > int(signal) or int(Mux.SEL_R15) < int(signal):
            raise MachineRuntimeError(
                f"invalid select register signal: {signal}")
        self.mux_left_out = signal

    def sel_right_reg(self, signal: Mux):
        self.mux_right_out = signal

    def get_left_out(self) -> int:
        return self.get_register_by_signal(self.mux_left_out)

    def get_right_out(self) -> int:
        return self.get_register_by_signal(self.mux_right_out)

    @staticmethod
    def get_register_by_signal(signal: Mux) -> int:
        signal_int = int(signal) - int(Mux.SEL_R0)
        if signal_int < 0 or signal_int > 15:
            raise MachineRuntimeError(
                f"Invalid select register signal: {signal}")
        return signal_int


class Alu:
    zero_flag: int

    result: int

    def __init__(self):
        self.result = 0
        self.zero_flag = 0

    def perform(self, in_left: int, in_right: int, operation: AluOperation) -> int:
        match operation:
            case AluOperation.ADD: self.result = in_left + in_right
            case AluOperation.SUB: self.result = in_left - in_right
            case AluOperation.MUL: self.result = in_left * in_right
            case AluOperation.AND: self.result = in_left & in_right
            case _:
                raise MachineRuntimeError(
                    f"operation {operation} not supported by alu")
        self.update_flags(self.result)
        return 0

    def update_flags(self, value: int):
        self.zero_flag = value == 0


class ControlUnit:
    rb: int  # 16 bit
    r1: int  # 16 bit
    r2: int  # 16 bit
    tick_count: int

    mpc: int

    address_out: int
    data_out: int

    mpc_mux: Mux
    operand_mux: Mux

    def __init__(self):
        self.rb = 0
        self.r1 = 0
        self.r2 = 0
        self.mpc = 0
        self.opcode_mux = self.OpcodeMux.Opcode

    def decode_instruction(self, instruction: str) -> None:
        opcode = int(instruction[0:7], 2)
        flag = int(instruction[-1], 2)
        print(opcode + flag)

    def set_address(self, address: int):
        self.address_out = address

    def set_data(self, data: int):
        self.data_out = data

    def tick(self):
        self.tick_count += 1


class IO:
    input_buffer: List[int]
    output_buffer: List[int]

    def __init__(self, input: str):
        self.input_buffer = list(map(ord, list(input)))  # str to int array
        self.output_buffer = []

    def latch_output(self, value: int):
        self.output_buffer[-1] = value

    def next_write_chr(self):
        self.output_buffer.append(0)

    def latch_input(self) -> int:
        return self.input_buffer[0]

    def next_read_chr(self):
        self.input_buffer.pop(0)


class DataMemory:
    cells: List[int]

    def __init__(self) -> None:
        self.cells = []

    def get_cell(self, index: int) -> int:
        return self.cells[index]

    def set_cell(self, index: int, value: int):
        self.cells[index] = value


class DataPath:
    data_memory: DataMemory
    register_file: RegisterFile
    alu: Alu
    control_unit: ControlUnit
    io_buffer: IO

    pc: int
    pc_mux: Mux

    data_src_mux: Mux
    data_src_mux2: Mux

    def __init__(self, input: str):
        self.pc = 0
        self.alu = Alu()
        self.register_file = RegisterFile()
        self.control_unit = ControlUnit()
        self.io_buffer = IO(input)
        self.data_memory = DataMemory()

    def latch_pc(self) -> None:
        match self.pc_mux:
            case Mux.PC_CU:
                self.pc = self.control_unit.address_out
            case Mux.PC_INC:
                self.pc += 1
            case _:
                raise MachineRuntimeError(f"invalid mux value {self.pc_mux}")

    def sel_pc(self, value: Mux):
        self.pc_mux = value

    def sel_data_src(self, value: Mux):
        self.data_src_mux = value

    def sel_data_src2(self, value: Mux):
        self.data_src_mux2 = value

    def get_data_src_mux_output(self) -> int:
        match self.data_src_mux:
            case Mux.SRC_MEM:
                return self.data_memory.get_cell(self.register_file.get_left_out())
            case Mux.SRC_ALU:
                return self.alu.result
            case _:
                raise MachineRuntimeError(
                    f"invalid mux value  {self.data_src_mux}")

    def get_data_src_mux2_output(self) -> int:
        match self.data_src_mux2:
            case Mux.SRC_CU:
                return self.control_unit.data_out
            case Mux.SRC_MUX:
                return self.get_data_src_mux_output()
            case _:
                raise MachineRuntimeError(
                    f"invalid mux value   {self.data_src_mux2}")


# def run_simulation(instruction_memory: List[str], data_memory: List[int], input: str):
#     datapath = DataPath(input=input)

#     control_unit = ControlUnit()

#     instruction_counter = 0


def read_file(file_name: str) -> List[str]:
    return open(file=file_name, mode='r').read().splitlines()


def prepare(compiled_data: str, compiled_code: str, input_file: str | None):
    print(read_file(compiled_data))
    print(read_file(compiled_code))
    if input_file is None:
        print("No input file provided!")
    else:
        print(read_file(input_file))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    if len(sys.argv) < 3:
        print("Not enought arguments!")
        print("Usage: python machine.py <compiled_code> <compiled_data> OP(<input_file>)")
        exit(1)

    prepare(sys.argv[1], sys.argv[2], None if len(
        sys.argv) < 4 else sys.argv[3])
