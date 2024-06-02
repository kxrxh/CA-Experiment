from enum import Enum

# Constatns:
INPUT_CELL_ADDRESS = 0
OUTPUT_CELL_ADDRESS = 1
DATA_MEMORY_BEGIN_ADDRESS = 2
INSTRUCTION_MEMORY_BEGIN_ADDRESS = 0

# Command binary representation (32 bit)
# | Opcode | RB   | R1 | Address/Number | Flag | Operation                |
# |--------|------|------------------|----------------|------|--------------------------|
# | 7 bits | 4 bits | 4 bits         | 16 bits        | 1 bit|           = 32 bit       |
# | Opcode | RB   | R1               | 16 * [0]       | 1    | Write word operation     |
# | Opcode | RB   | R1               | 16 * [0]       | 0    | Load word operation      |
# | Opcode | RB   | R1               | R2             | 0    | Math operations (reg-reg)|
# | Opcode | RB   | R1               | Number         | 1    | Math operations (reg-imm)|
# | Opcode | RB   | R1               | Address        | 0    | Branch operations        |
# | Opcode | 0000 | 0000             | Address        | 1    | Branch (Jump) operation  |
# | Opcode | 0000 | 0000             | 16 * [0]       | 0    | HALT/NOP operation       |


class Opcode(Enum):
    NOP = ("nop", 0)
    HALT = ("halt", 0b1111111)

    # Memory ops
    LOAD_WORD = ("lw", 1)
    WRITE_WORD = ("sw", 2)

    # Math/logic ops
    ADD = ("add", 3)
    SUB = ("sub", 4)
    MUL = ("mul", 5)
    AND = ("and", 6)

    # Branch ops
    BEQ = ("beq", 7)
    BNE = ("bne", 8)
    BLT = ("blt", 9)
    BGT = ("bgt", 10)
    JUMP = ("jmp", 11)

    def __init__(self, mnemonic: str, code: int):
        """
        Initializes an Opcode enum member.

        Parameters:
            mnemonic (str): The mnemonic string for the opcode.
            code (int): The binary code for the opcode.
        """

        self.mnemonic = mnemonic
        self.code: int = code

    def get_code(self) -> int:
        """
        Returns the binary code of the opcode.

        Returns:
            int: The binary code of the opcode.
        """
        return self.code

    def is_memory(self) -> bool:
        """
        Checks if the opcode is a lw or ww operation.

        Returns:
            bool: True if the opcode is a load or store operation, False otherwise.
        """
        return self in [Opcode.LOAD_WORD, Opcode.WRITE_WORD]

    def is_branch(self) -> bool:
        """
        Checks if the opcode is a branch operation.

        Returns:
            bool: True if the opcode is a branch operation, False otherwise.
        """
        return self in [Opcode.BEQ, Opcode.BNE, Opcode.BLT, Opcode.BGT, Opcode.JUMP]

    def is_mathlog(self) -> bool:
        """
        Checks if the opcode is a math/logic operation.

        Returns:
            bool: True if the opcode is a math/logic operation, False otherwise.
        """
        return self in [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.AND]

    def is_no_args(self) -> bool:
        """
        Checks if the opcode requires no arguments.

        Returns:
            bool: True if the opcode requires no arguments, False otherwise.
        """
        return self in [Opcode.NOP, Opcode.HALT]

    @staticmethod
    def get_opcode_by_mnemonic(value: str) -> "Opcode":
        """
        Returns the Opcode enum member corresponding to the given mnemonic string.

        Parameters:
            value (str): The mnemonic string of the opcode.

        Returns:
            Opcode: The Opcode enum member corresponding to the mnemonic string.

        Raises:
            ValueError: If no opcode matches the given mnemonic string.
        """
        for opcode in Opcode:
            if value == opcode.value[0]:
                return opcode
        raise ValueError(f"No such opcode: {value}")
