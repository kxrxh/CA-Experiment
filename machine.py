# class MicroProgram:
#     def __init__(self):
#         self.microprograms = {}

#     def add_microprogram(self, instruction, microprogram):
#         self.microprograms[instruction] = microprogram

#     def get_microprogram(self, instruction):
#         return self.microprograms.get(instruction, [])

class RegisterFile:
    r0: int
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
    rl: int
    rs: int
    rd: int
    rip: int
    rpc: int

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
        self.rl = 0  # Load register
        self.rs = 0  # Store register
        self.rd = 0  # Data register
        self.rip = 0  # ??
        self.rpc = 0  # ??


class Alu:
    def __init__(self):
        self.zero_flag = False

    def perform(self, in_left: int, in_right: int, op_code) -> int:

        return 0

    def update_flags(self, value: int):
        self.zero_flag = value == 0


# class ControlUnit:
#     def __init__(self):
#         self.op1 = 0
#         self.op2 = 0
#         self.tmp = 0

#         self.pc = 0

#     def execute_micro_instruction(self, micro_instruction: str):
#         if micro_instruction == "fetch":
#             self.pc += 1
#         elif micro_instruction == "decode":
#             self.pc += 1
#         elif micro_instruction == "load_op1":
#             self.pc += 1
#         elif micro_instruction == "load_op2":
#             self.pc += 1
#         elif micro_instruction == "store_op0":
#             self.pc += 1
#         elif micro_instruction == "add":
#             self.tmp = self.op1 + self.op2
#         elif micro_instruction == "sub":
#             self.pc += 1
#         elif micro_instruction == "mul":
#             self.pc += 1
#         elif micro_instruction == "div":
#             self.pc += 1
#         elif micro_instruction == "halt":
#             self.pc += 1
#         else:
#             raise RuntimeError("Invalid micro instruction")


# class DataPath:
#     def __init__(self):
#         self.registers = [0 for _ in range(16)]
#         self.pc = 0
#         self.tick_count = 0
#         self.alu = Alu()
