from enum import Enum
# Command binary representation:
# | 6      | 6   | 6   |  12    | 1 |
# | Opcode | RB  | RS1 | RS2    | S | <--- Math operations
# | Opcode | RB  | RS1 | OFFSET | S | <--- Branch operations
# | Opcode | RB  |    Address   | S | <--- Jump operation
# | Opcode | ----------------- | S | <--- HALT operation


class Opcode(Enum):
    NOP = ("nop", 0)
    MOVE = ("move", 1)
    LOAD = ("load", 2)
    STORE = ("store", 3)



    ADD = ("add", 4)
    SUB = ("sub", 5)
    MUL = ("mul", 6)
    DIV = ("div", 7)

    

    BEQ = ("beq", 8)
    BNE = ("bne", 9)
    BLT = ("blt", 10)
    BGT = ("bgt", 11)
    
    JUMP = ("jmp", "")

    HALT = ("hlt", 0b111111)

    def __init__(self, mnemonic: str, code: str):
        self.mnemonic = mnemonic
        self.code = code
    

def register_to_binary(index: int):
    return f"{index:04b}"

