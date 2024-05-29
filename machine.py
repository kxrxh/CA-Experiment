# class MicroProgram:
#     def __init__(self):
#         self.microprograms = {}

#     def add_microprogram(self, instruction, microprogram):
#         self.microprograms[instruction] = microprogram

#     def get_microprogram(self, instruction):
#         return self.microprograms.get(instruction, [])

import logging
import sys
from typing import List

from machine_error import InvalidRegisterIndex


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

    reg_left_out: int
    reg_right_out: int

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
        self.r13 = 0  # ?? Data register
        self.r14 = 0  # ??
        self.r15 = 0  # ??

        self.reg_left_out = 0
        self.reg_right_out = 0

    def latch_reg_n(self, index: int, value: int) -> None:
        if index == 0:
            raise InvalidRegisterIndex("register with index 0 is immutable")
        elif 1 <= index <= 15:
            setattr(self, f"r{index}", value)
        else:
            raise InvalidRegisterIndex(f"register r{index} does not exist")

    def sel_left_reg(self, index: int):
        if index < 0 or index > 15:
            raise InvalidRegisterIndex(f"register r{index} does not exist")
        self.reg_left_out = getattr(self, f"r{index}")

    def sel_right_reg(self, index: int):
        if index < 0 or index > 15:
            raise InvalidRegisterIndex(f"register r{index} does not exist")
        self.reg_right_out = getattr(self, f"r{index}")


class Alu:
    zero_flag: int

    def __init__(self):
        self.zero_flag = 0

    def perform(self, in_left: int, in_right: int, operation: int) -> int:
        result: int = 0

        self.update_flags(result)
        return 0

    def update_flags(self, value: int):
        self.zero_flag = value == 0


class ControlUnit:
    def __init__(self):
        self.op1 = 0
        self.op2 = 0
        self.tmp = 0

        self.pc = 0

    def execute_micro_instruction(self, micro_instruction: str):
        if micro_instruction == "fetch":
            self.pc += 1
        elif micro_instruction == "decode":
            self.pc += 1
        elif micro_instruction == "load_op1":
            self.pc += 1
        elif micro_instruction == "load_op2":
            self.pc += 1
        elif micro_instruction == "store_op0":
            self.pc += 1
        elif micro_instruction == "add":
            self.tmp = self.op1 + self.op2
        elif micro_instruction == "sub":
            self.pc += 1
        elif micro_instruction == "mul":
            self.pc += 1
        elif micro_instruction == "div":
            self.pc += 1
        elif micro_instruction == "halt":
            self.pc += 1
        else:
            raise RuntimeError("Invalid micro instruction")


class DataPath:
    register_file: RegisterFile
    alu: Alu
    pc: int

    def __init__(self):
        self.pc = 0
        self.tick_count = 0
        self.alu = Alu()
        self.register_file = RegisterFile()


def run_simulation(instruction_memory: List[str], data_memory: List[int]):
    datapath = DataPath()

    control_unit = ControlUnit()

    instruction_counter = 0


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
