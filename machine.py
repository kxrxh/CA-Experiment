class MicroProgram:
    def __init__(self):
        self.microprograms = {}

    def add_microprogram(self, instruction, microprogram):
        self.microprograms[instruction] = microprogram

    def get_microprogram(self, instruction):
        return self.microprograms.get(instruction, [])

class Alu:
    def __init__(self):
        self.zero_flag = False
        self.negative_flag = False

    def perform(self, in_left: int, in_right: int, op_code) -> int:

        return 0

    def update_flags(self, value: int):
        if value == 0:
            self.zero_flag = True
            return

        self.zero_flag = False

        if value < 0:
            self.negative_flag = True
        else:
            self.negative_flag = False


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
    def __init__(self):
        self.registers = [0 for _ in range(16)]
        self.pc = 0
        self.tick_count = 0
        self.alu = Alu()
