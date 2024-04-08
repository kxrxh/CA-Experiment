from dataclasses import dataclass, field
from typing import List, Union

@dataclass
class Instruction:
    opcode: int = field(default_factory=int)
    command: str = field(default_factory=str)
    operands: List[int] = field(default_factory=list)


class InstructionMemory:
    def __init__(self, size: int):
        self.memory: List[Instruction] = [Instruction() for _ in range(size)]

    def read(self, address: int) -> Instruction:
        return self.memory[address]

    def write(self, address: int, instruction: Instruction) -> None:
        self.memory[address] = instruction

class DataMemory:
    def __init__(self, size: int):
        self.memory: List[Union[int, bytes]] = [0] * size
        self.next_str_address: int = 0
    
    def read(self, address: int) -> Union[int, bytes]:
        return self.memory[address]
    
    def write(self, address: int, data: Union[int, bytes]) -> None:
        self.memory[address] = data
    
    def allocate_str(self, string: str) -> int:
        start_address = self.next_str_address
        string_bytes = string.encode()
        self.memory[start_address:start_address+len(string_bytes)] = string_bytes
        self.memory[start_address+len(string_bytes)] = 0  # null terminator
        self.next_str_address += len(string_bytes) + 1
        return start_address
                
                