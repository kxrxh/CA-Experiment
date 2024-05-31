from machine_exceptions import InvalidRegisterIndex
from microcode_new import Signal


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
    r11: int
    r12: int
    r13: int
    r14: int
    r15: int   # Register for temp values

    mux_left_out: Signal
    left_out: int

    mux_right_out: Signal
    right_out: int

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

        self.mux_left_out = Signal.SEL_L_REG0
        self.mux_right_out = Signal.SEL_R_REG0
        self.left_out = 0
        self.right_out = 0

    def latch_reg_n(self, index: int, value: int) -> None:
        if index == 0:
            raise InvalidRegisterIndex("register with index 0 is immutable")
        elif 1 <= index <= 15:
            setattr(self, f"r{index}", value)
        else:
            raise InvalidRegisterIndex(f"register r{index} does not exist")

    def sel_left_reg(self, signal: Signal):
        self.mux_left_out = signal
        register_index = int(signal) - int(Signal.SEL_L_REG0)
        self.left_out = getattr(self, f"r{register_index}")

    def sel_right_reg(self, signal: Signal):
        self.mux_right_out = signal
        register_index = int(signal) - int(Signal.SEL_R_REG0)
        self.right_out = getattr(self, f"r{register_index}")
