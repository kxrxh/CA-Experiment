from enum import IntEnum, auto
from typing import List


class Signal(IntEnum):
    """Enum class representing signals."""
    HALT = 0
    LATCH_REG = auto()
    LATCH_REG0 = auto()
    LATCH_REG1 = auto()
    LATCH_REG2 = auto()
    LATCH_REG3 = auto()
    LATCH_REG4 = auto()
    LATCH_REG5 = auto()
    LATCH_REG6 = auto()
    LATCH_REG7 = auto()
    LATCH_REG8 = auto()
    LATCH_REG9 = auto()
    LATCH_REG10 = auto()
    LATCH_REG11 = auto()
    LATCH_REG12 = auto()
    LATCH_REG13 = auto()
    LATCH_REG14 = auto()
    LATCH_REG15 = auto()

    ALU_ADD = auto()
    ALU_SUB = auto()
    ALU_AND = auto()
    ALU_MUL = auto()

    LATCH_PC = auto()
    LATCH_MPC = auto()
    LATCH_IR = auto()
    LATCH_OPERANDS = auto()

    LATCH_READ_MEM = auto()
    LATCH_WRITE_MEM = auto()

    SEL_PC_ADDR = auto()
    SEL_PC_INC = auto()

    SEL_MPC_ZERO = auto()
    SEL_MPC_INC = auto()
    SEL_MPC_IR = auto()

    SEL_SRC_MEM = auto()
    SEL_SRC_ALU = auto()
    SEL_SRC_CU = auto()

    SEL_REG_L = auto()
    SEL_REG_R = auto()

    SEL_L_REG0 = auto()
    SEL_L_REG1 = auto()
    SEL_L_REG2 = auto()
    SEL_L_REG3 = auto()
    SEL_L_REG4 = auto()
    SEL_L_REG5 = auto()
    SEL_L_REG6 = auto()
    SEL_L_REG7 = auto()
    SEL_L_REG8 = auto()
    SEL_L_REG9 = auto()
    SEL_L_REG10 = auto()
    SEL_L_REG11 = auto()
    SEL_L_REG12 = auto()
    SEL_L_REG13 = auto()
    SEL_L_REG14 = auto()
    SEL_L_REG15 = auto()

    SEL_R_REG0 = auto()
    SEL_R_REG1 = auto()
    SEL_R_REG2 = auto()
    SEL_R_REG3 = auto()
    SEL_R_REG4 = auto()
    SEL_R_REG5 = auto()
    SEL_R_REG6 = auto()
    SEL_R_REG7 = auto()
    SEL_R_REG8 = auto()
    SEL_R_REG9 = auto()
    SEL_R_REG10 = auto()
    SEL_R_REG11 = auto()
    SEL_R_REG12 = auto()
    SEL_R_REG13 = auto()
    SEL_R_REG14 = auto()
    SEL_R_REG15 = auto()


class MicroProgramMemory:
    """Class representing microprogram memory."""
    _memory: List[List[Signal]] = [
        # 0: Instruction fetch
        [Signal.SEL_MPC_INC, Signal.LATCH_MPC,
         Signal.SEL_PC_INC, Signal.LATCH_PC],
        [Signal.SEL_MPC_INC, Signal.LATCH_MPC,
         Signal.LATCH_IR, Signal.LATCH_OPERANDS],
        [Signal.SEL_MPC_IR, Signal.LATCH_PC],

        # 3: Nop
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC],

        # 4: Halt
        [Signal.HALT],

        # 5: Add no-flag
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC, Signal.ALU_ADD,
         Signal.SEL_REG_L, Signal.SEL_REG_R, Signal.SEL_SRC_ALU, Signal.LATCH_REG0],

        # 6: Add with flag
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC,
         Signal.SEL_SRC_CU, Signal.LATCH_REG15],
        [Signal.SEL_MPC_INC, Signal.LATCH_MPC, Signal.ALU_ADD,
         Signal.SEL_REG_L, Signal.SEL_R_REG15, Signal.SEL_SRC_ALU, Signal.LATCH_REG0],

        # 8: Sub no-flag
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC, Signal.ALU_SUB,
         Signal.SEL_REG_L, Signal.SEL_REG_R, Signal.SEL_SRC_ALU, Signal.LATCH_REG0],

        # 9: Sub with flag
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC,
         Signal.SEL_SRC_CU, Signal.LATCH_REG15],
        [Signal.SEL_MPC_INC, Signal.LATCH_MPC, Signal.ALU_SUB,
         Signal.SEL_REG_L, Signal.SEL_R_REG15, Signal.SEL_SRC_ALU, Signal.LATCH_REG0],

        # 11: Mul no-flag
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC, Signal.ALU_MUL,
         Signal.SEL_REG_L, Signal.SEL_REG_R, Signal.SEL_SRC_ALU, Signal.LATCH_REG0],

        # 12: Mul with flag
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC,
         Signal.SEL_SRC_CU, Signal.LATCH_REG15],
        [Signal.SEL_MPC_INC, Signal.LATCH_MPC, Signal.ALU_MUL,
         Signal.SEL_REG_L, Signal.SEL_R_REG15, Signal.SEL_SRC_ALU, Signal.LATCH_REG0],

        # 14: And with no-flag
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC, Signal.ALU_AND,
         Signal.SEL_REG_L, Signal.SEL_REG_R, Signal.SEL_SRC_ALU, Signal.LATCH_REG0],

        # 15: And with flag
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC,
         Signal.SEL_SRC_CU, Signal.LATCH_REG15],
        [Signal.SEL_MPC_INC, Signal.LATCH_MPC, Signal.ALU_AND,
         Signal.SEL_REG_L, Signal.SEL_R_REG15, Signal.SEL_SRC_ALU, Signal.LATCH_REG0],

        # 17: lw
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC, Signal.SEL_SRC_CU,
         Signal.SEL_REG_L, Signal.LATCH_READ_MEM],
        [Signal.SEL_MPC_INC, Signal.LATCH_MPC,
         Signal.SEL_SRC_MEM, Signal.LATCH_REG0],

        # 19: sw
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC,
         Signal.SEL_SRC_CU, Signal.LATCH_REG15],
        [Signal.SEL_MPC_INC, Signal.LATCH_MPC, Signal.SEL_REG_L, Signal.SEL_R_REG15,
         Signal.LATCH_WRITE_MEM],
    ]

    @staticmethod
    def get_microprogram(index: int) -> List[Signal]:
        """Retrieve microprogram for a given index."""
        return MicroProgramMemory._memory[index]
