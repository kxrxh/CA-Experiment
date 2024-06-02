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

    SEL_TWICE_INC_IF_Z = auto()
    SEL_TWICE_INC_IF_N = auto()
    SEL_ONE_INC = auto()

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
        [Signal.SEL_ONE_INC, Signal.SEL_PC_INC, Signal.LATCH_PC, Signal.SEL_MPC_INC, Signal.LATCH_MPC],
        [Signal.SEL_MPC_INC, Signal.LATCH_MPC, Signal.LATCH_IR, Signal.LATCH_OPERANDS],
        [Signal.SEL_MPC_IR, Signal.LATCH_MPC],
        # 3: Nop
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC],
        # 4: Halt
        [Signal.HALT],
        # 5: Add no-flag
        [
            Signal.SEL_REG_L,
            Signal.SEL_REG_R,
            Signal.ALU_ADD,
            Signal.SEL_SRC_ALU,
            Signal.LATCH_REG,
            Signal.SEL_MPC_ZERO,
            Signal.LATCH_MPC,
        ],
        # 6: Add with flag
        [Signal.SEL_SRC_CU, Signal.LATCH_REG15, Signal.SEL_MPC_INC, Signal.LATCH_MPC],
        [
            Signal.SEL_REG_L,
            Signal.SEL_R_REG15,
            Signal.ALU_ADD,
            Signal.SEL_SRC_ALU,
            Signal.LATCH_REG,
            Signal.SEL_MPC_ZERO,
            Signal.LATCH_MPC,
        ],
        # 8: Sub no-flag
        [
            Signal.SEL_REG_L,
            Signal.SEL_REG_R,
            Signal.ALU_SUB,
            Signal.SEL_SRC_ALU,
            Signal.LATCH_REG,
            Signal.SEL_MPC_ZERO,
            Signal.LATCH_MPC,
        ],
        # 9: Sub with flag
        [Signal.SEL_SRC_CU, Signal.LATCH_REG15, Signal.SEL_MPC_INC, Signal.LATCH_MPC],
        [
            Signal.SEL_REG_L,
            Signal.SEL_R_REG15,
            Signal.ALU_SUB,
            Signal.SEL_SRC_ALU,
            Signal.LATCH_REG,
            Signal.SEL_MPC_ZERO,
            Signal.LATCH_MPC,
        ],
        # 11: Mul no-flag
        [
            Signal.SEL_REG_L,
            Signal.SEL_REG_R,
            Signal.ALU_MUL,
            Signal.SEL_SRC_ALU,
            Signal.LATCH_REG,
            Signal.SEL_MPC_ZERO,
            Signal.LATCH_MPC,
        ],
        # 12: Mul with flag
        [Signal.SEL_SRC_CU, Signal.LATCH_REG15, Signal.SEL_MPC_INC, Signal.LATCH_MPC],
        [
            Signal.SEL_REG_L,
            Signal.SEL_R_REG15,
            Signal.ALU_MUL,
            Signal.SEL_SRC_ALU,
            Signal.LATCH_REG,
            Signal.SEL_MPC_ZERO,
            Signal.LATCH_MPC,
        ],
        # 14: And with no-flag
        [
            Signal.SEL_REG_L,
            Signal.SEL_REG_R,
            Signal.ALU_AND,
            Signal.SEL_SRC_ALU,
            Signal.LATCH_REG,
            Signal.SEL_MPC_ZERO,
            Signal.LATCH_MPC,
        ],
        # 15: And with flag
        [Signal.SEL_SRC_CU, Signal.LATCH_REG15, Signal.SEL_MPC_INC, Signal.LATCH_MPC],
        [
            Signal.SEL_REG_L,
            Signal.SEL_R_REG15,
            Signal.ALU_AND,
            Signal.SEL_SRC_ALU,
            Signal.LATCH_REG,
            Signal.SEL_MPC_ZERO,
            Signal.LATCH_MPC,
        ],
        # 17: lw
        [Signal.SEL_SRC_CU, Signal.SEL_REG_L, Signal.LATCH_READ_MEM, Signal.SEL_MPC_INC, Signal.LATCH_MPC],
        [Signal.SEL_SRC_MEM, Signal.LATCH_REG, Signal.SEL_MPC_ZERO, Signal.LATCH_MPC],
        # 19: sw
        [Signal.SEL_REG_L, Signal.SEL_REG_R, Signal.LATCH_WRITE_MEM, Signal.SEL_MPC_ZERO, Signal.LATCH_MPC],
        # 20: beq
        [Signal.SEL_REG_L, Signal.SEL_REG_R, Signal.ALU_SUB, Signal.SEL_MPC_INC, Signal.LATCH_MPC],
        [Signal.SEL_MPC_INC, Signal.SEL_TWICE_INC_IF_Z, Signal.LATCH_MPC],
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC],  # if not Z
        [Signal.SEL_PC_ADDR, Signal.LATCH_PC, Signal.SEL_MPC_ZERO, Signal.LATCH_MPC],  # if Z
        # 24: bne
        [Signal.SEL_REG_L, Signal.SEL_REG_R, Signal.ALU_SUB, Signal.SEL_MPC_INC, Signal.LATCH_MPC],
        [Signal.SEL_MPC_INC, Signal.SEL_TWICE_INC_IF_Z, Signal.LATCH_MPC],
        [Signal.SEL_PC_ADDR, Signal.LATCH_PC, Signal.SEL_MPC_ZERO, Signal.LATCH_MPC],  # if not Z
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC],  # if Z
        # 28: bgt
        [Signal.SEL_REG_L, Signal.SEL_REG_R, Signal.ALU_SUB, Signal.SEL_MPC_INC, Signal.LATCH_MPC],
        [Signal.SEL_MPC_INC, Signal.SEL_TWICE_INC_IF_N, Signal.LATCH_MPC],
        [Signal.SEL_PC_ADDR, Signal.LATCH_PC, Signal.SEL_MPC_ZERO, Signal.LATCH_MPC],  # if not N
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC],  # if N
        # 32: blt
        [Signal.SEL_REG_L, Signal.SEL_REG_R, Signal.ALU_SUB, Signal.SEL_MPC_INC, Signal.LATCH_MPC],
        [Signal.SEL_MPC_INC, Signal.SEL_TWICE_INC_IF_N, Signal.LATCH_MPC],
        [Signal.SEL_MPC_ZERO, Signal.LATCH_MPC],  # if not N
        [Signal.SEL_PC_ADDR, Signal.LATCH_PC, Signal.SEL_MPC_ZERO, Signal.LATCH_MPC],  # if N
        # 36: jmp
        [Signal.SEL_PC_ADDR, Signal.LATCH_PC, Signal.SEL_MPC_ZERO, Signal.LATCH_MPC],
        [Signal.SEL_MPC_INC, Signal.LATCH_MPC],
    ]

    @staticmethod
    def get_microprogram(index: int) -> List[Signal]:
        """Retrieve microprogram for a given index."""
        return MicroProgramMemory._memory[index]
