from register_file import RegisterFile
from microcode import Signal

MAX_NUMBER = 1 << 31 - 1
MIN_NUMBER = -(1 << 31)


class Alu:
    reg_file: RegisterFile
    alu_signal: Signal
    alu_result: int

    neg_zero: int

    def __init__(self, reg_file: RegisterFile):
        self.result = 0
        self.neg_zero = 0  # 2 bits 'NZ'
        self.reg_file = reg_file

    def sel_alu(self, signal: Signal):
        self.alu_signal = signal
        self.get_alu_by_signal(self.alu_signal)

    def get_alu_by_signal(self, signal: Signal):
        match signal:
            case Signal.ALU_ADD:
                self.alu_result = self.reg_file.left_out + self.reg_file.right_out
            case Signal.ALU_SUB:
                self.alu_result = self.reg_file.left_out - self.reg_file.right_out
            case Signal.ALU_MUL:
                self.alu_result = self.reg_file.left_out * self.reg_file.right_out
            case Signal.ALU_AND:
                self.alu_result = self.reg_file.left_out & self.reg_file.right_out
        self._handle_overflow()
        self.update_flags(self.alu_result)

    def _handle_overflow(self):
        if self.alu_result > MAX_NUMBER:
            self.alu_result %= MAX_NUMBER
        elif self.alu_result < MIN_NUMBER:
            self.alu_result %= abs(MIN_NUMBER)

    def update_flags(self, value: int):
        if value == 0:
            self.neg_zero = 1  # '01'
        elif value < 0:
            self.neg_zero = 2  # '10'
        else:
            self.neg_zero = 0  # '00'
