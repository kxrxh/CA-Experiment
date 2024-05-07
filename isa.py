from enum import Enum
# | 7      | 6   | 6   |  12    | 1 |
# | Opcode | RB  | RS1 | RS2    | S | <--- Math operations
# | Opcode | RB  | RS1 | OFFSET | S | <--- Branch operations
# | Opcode | RB  |    Address   | S | <--- Jump operation
# | Opcode | ------------------ | S | <--- HALT operation


class Opcode(Enum):
    NOP = ("nop", "0000000")
    LOAD = ("load", "0000001")
    STORE = ("store", "0000010")

    ADD = ("add", "0000100")
    SUB = ("sub", "0000101")
    MUL = ("mul", "0000110")
    DIV = ("div", "0000111")

    BEQ = ("beq", "0001000")
    BNE = ("bne", "0001001")
    BLT = ("blt", "0001010")
    BGT = ("bgt", "0001011")
    
    JUMP = ("jmp", "0001000")

    HALT = ("hlt", "1100000")

    def __init__(self, mnemonic: str, code: str):
        self.mnemonic = mnemonic
        self.code = code
    

def register_to_binary(index: int):
    return f"{index:04b}"

