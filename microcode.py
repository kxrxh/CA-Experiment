from enum import Enum


class Latch(Enum):
    PC = 0


class AluOperation(Enum):
    ADD = 1
    SUB = 2
    AND = 3
    OR = 4
    XOR = 5
    MUL = 6
    MOD = 7

    