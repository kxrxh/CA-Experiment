from enum import Enum

# Constatns:
INPUT_CELL_ADDRESS = 1
OUTPUT_CELL_ADDRESS = 2


# Command binary representation (32 bit)
# | 7      | 4   |  4  |   16    | Flag|
# | Opcode | RB  | 0000| ADDRESS | 0/1| -- 0 for read / 1 for write
# | Opcode | RB  | RS1 | RS2     | 0 |<--- Math operations
# | Opcode | RB  | RS1 | VALUE   | 1 | <--- Math operations
# | Opcode | RB  | RS1 | LABEL   | 0 | <--- Branch operations
# | Opcode | 1111|1111 | Address | 1 |<--- Branch(Jump) operation
# | Opcode | ------------------- | - | <--- HALT/NOP operation


class Opcode(Enum):
    NOP = ("nop", 0)
    HALT = ("halt", 0b1111111)

    # Memory ops
    LOAD = ("load", 1)
    STORE = ("store", 2)

    # Math ops
    ADD = ("add", 3)
    SUB = ("sub", 4)
    MUL = ("mul", 5)
    DIV = ("div", 6)

    # Branch ops
    BEQ = ("beq", 7)
    BNE = ("bne", 8)
    BLT = ("blt", 9)
    BGT = ("bgt", 10)
    JUMP = ("jmp", 11)

    def __init__(self, mnemonic: str, code: str):
        self.mnemonic = mnemonic
        self.code = code

    @staticmethod
    def str_to_opcode(value: str) -> 'Opcode':
        for opcode in Opcode:
            if value == opcode.value[0]:
                return opcode
        raise ValueError(f"No such opcode: {value}")


def register_to_binary(index: int):
    return f"{index:06b}"


def integer_to_binary(number: int):
    return f"{number:16b}"
