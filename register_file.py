from machine_exceptions import InvalidRegisterIndex
from microcode import Signal


class RegisterFile:
    def __init__(self):
        self.registers = [0] * 16  # Initialize registers r0 to r15 with 0
        self.mux_left_out = Signal.SEL_L_REG0
        self.mux_right_out = Signal.SEL_R_REG0
        self.left_out = 0
        self.right_out = 0

    def latch_reg_n(self, index: int, value: int) -> None:
        if index == 0:
            raise InvalidRegisterIndex("Register with index 0 is immutable")
        elif 1 <= index <= 15:
            self.registers[index] = value
        else:
            raise InvalidRegisterIndex(f"Register r{index} does not exist")

    def sel_left_reg(self, signal: Signal) -> None:
        self.mux_left_out = signal
        register_index = int(signal) - int(Signal.SEL_L_REG0)
        self.left_out = self.registers[register_index]

    def sel_right_reg(self, signal: Signal) -> None:
        self.mux_right_out = signal
        register_index = int(signal) - int(Signal.SEL_R_REG0)
        self.right_out = self.registers[register_index]
