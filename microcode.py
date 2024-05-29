from enum import Enum, IntEnum


# Signals
class Latch(IntEnum):
    R0 = 0
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5
    R6 = 6
    R7 = 7
    R8 = 8
    R9 = 9
    R10 = 10
    R11 = 11
    R12 = 12
    R13 = 13
    R14 = 14
    R15 = 15

    PC = 16

    WRITE_BUF = 17
    READ_BUF = 18

    NEXT_READ_CH = 19
    NEXT_WRITE_CH = 20

    MPC = 21

    IR = 22


class AluOperation(IntEnum):
    ADD = 1
    SUB = 2
    MUL = 3
    AND = 4

class Halt(IntEnum):
    pass

class Mux(IntEnum):
    PC_CU = 0
    PC_INC = 1

    SRC_MEM = 2
    SRC_ALU = 3

    SRC_CU = 4
    SRC_MUX = 5

    SEL_R0 = 6
    SEL_R1 = 7
    SEL_R2 = 8
    SEL_R3 = 9
    SEL_R4 = 10
    SEL_R5 = 11
    SEL_R6 = 12
    SEL_R7 = 13
    SEL_R8 = 14
    SEL_R9 = 15
    SEL_R10 = 16
    SEL_R11 = 17
    SEL_R12 = 18
    SEL_R13 = 19
    SEL_R14 = 20
    SEL_R15 = 21

    MPC_ZERO = 22
    MPC_INC = 23
    MPC_IR = 24

    OP_RB = 25
    OP_R1 = 26
    OP_R2 = 27


# Microcommands
mc_memory = [
    # Instruction fetch
    [Mux.MPC_INC, Latch.MPC, Mux.MPC_INC, Latch.PC],
    [Mux.MPC_INC, Latch.MPC, Latch.IR],
    [Mux.MPC_IR, Latch.PC],
    
    # 3: Nop
    [Mux.MPC_ZERO, Latch.MPC],

    # 4: Halt
    [Halt(0)],

    # 5: Add no-flag
    [Mux.MPC_ZERO, Latch.MPC, AluOperation.ADD],
]
