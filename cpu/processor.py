from cpu.memory import DataMemory, Instruction, InstructionMemory


class Processor:
    def __init__(self, instruction_memory, data_memory):
        self.instruction_memory = instruction_memory
        self.data_memory = data_memory
        self.registers = [Register(i, 0) for i in range(16)]
        self.program_counter = 0
        self.flags = {'zero': False, 'negative': False,
                      'overflow': False, 'carry': False}
        self.instruction_set = {
            'nop': self.execute_nop,
            'add': self.execute_add,
            'sub': self.execute_sub,
            'mul': self.execute_mul,
            'div': self.execute_div,
            'and': self.execute_and,
            'or': self.execute_or,
            'xor': self.execute_xor,
            'not': self.execute_not,
            'jmp': self.execute_jmp,
            'jz': self.execute_jz,
            'jnz': self.execute_jnz,
            'beq': self.execute_beq,
            'bne': self.execute_bne,
            'bgt': self.execute_bgt,
            'blt': self.execute_blt,
            'halt': self.execute_halt,
        }

    def run(self):
        while (True):
            instruction = self.instruction_memory[self.program_counter]
            self.program_counter += 1
            self.execute(instruction)

    def fetch_instruction(self) -> Instruction:
        instruction = self.instruction_memory.read(self.program_counter)
        self.program_counter += 1
        return instruction

    def execute_instruction(self, instruction: Instruction):
        self.instruction_set[instruction.name](instruction)

    def decode_instruction(self, instruction_word: int) -> Instruction:
        opcode = (instruction_word >> 28) & 0xF
        operands = []
        for i in range((instruction_word >> 24) & 0xF):
            operands.append((instruction_word >> (i * 4)) & 0xF)
        return Instruction(self.instruction_set_names[opcode], operands)
    
    def update_flags(self, result: int):
        self.flags['zero'] = result == 0
        self.flags['negative'] = result < 0
        self.flags['overflow'] = self.registers[1] != 0 and self.registers[0] < 0
        self.flags['carry'] = result > 2**32 - 1
        self.flags['overflow'] = result != 0 and self.flags['carry']


class Register:
    def __init__(self, index, value):
        self.index = index
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

if __name__ == "__main__":
    instruction_memory = InstructionMemory()
    data_memory = DataMemory()
    cpu = Processor(instruction_memory=instruction_memory, data_memory=data_memory)
    cpu.run()