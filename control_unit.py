from alu import Alu
from datapath import DataPath
from isa import Opcode
from machine_exceptions import MachineRuntimeError
from microcode import MicroProgramMemory, Signal


class ControlUnit:
    """
    The ControlUnit is responsible for controlling the flow of execution
    in the CPU. It decodes instructions, generates control signals, and manages
    the program counter and registers.
    """

    alu: Alu
    datapath: DataPath

    ir: int  # Instruction register
    operands: int  # Operands (24 bit register)

    mpc_mux: Signal
    mpc: int  # MP counter

    inc_value: int

    tick_counter: int

    def __init__(self, alu: Alu, datapath: DataPath):
        """
        Initialize the ControlUnit with an ALU and a DataPath.

        Args:
            alu (Alu): The ALU instance to be used by the ControlUnit.
            datapath (DataPath): The DataPath instance to be used by the ControlUnit.
        """
        self.ir = 0
        self.operands = 0
        self.mpc = 0
        self.alu = alu
        self.datapath = datapath
        self.tick_counter = 0

        self.inc_value = 1

    def latch_operands(self, instruction: str) -> None:
        """
        Latch the operands from the given instruction.

        Args:
            instruction (str): The instruction string.
        """
        self.operands = int(instruction[7:-1], 2)
        self.datapath.cu_data_out = int(instruction[7+4+4:-1], 2)
        self.datapath.cu_address_out = int(instruction[7+4+4:-1], 2)

    def decode_instruction(self, instruction: str) -> None:
        """
        Decode the given instruction and set the decode_line attribute accordingly.

        Args:
            instruction (str): The instruction string to be decoded.
        """

        # Extract opcode and flag from the instruction
        opcode = int(instruction[0:7], 2)
        flag = int(instruction[-1], 2)

        # Mapping of opcode and flag to decode lines
        opcode_flag_map = {
            Opcode.NOP.code: {0: 3, 1: 3},
            Opcode.HALT.code: {0: 4, 1: 4},
            Opcode.ADD.code: {0: 5, 1: 6},
            Opcode.SUB.code: {0: 8, 1: 9},
            Opcode.MUL.code: {0: 11, 1: 12},
            Opcode.AND.code: {0: 14, 1: 15},
            Opcode.LOAD_WORD.code: {0: 17, 1: 17},
            Opcode.WRITE_WORD.code: {0: 19, 1: 19},
            Opcode.BEQ.code: {0: 20,  1:  20},
            Opcode.BNE.code: {0: 24,  1: 24},
            Opcode.BGT.code:  {0:  28,  1:  28},
            Opcode.BLT.code:   {0:  32,  1:  32},
            Opcode.JUMP.code: {0: 36, 1: 36},
        }

        self.decode_line = opcode_flag_map[opcode][flag]

    def tick(self):
        """
        Increment the tick counter.
        """
        self.tick_counter += 1

    def latch_mpc(self):
        """
        Latch the MPC (Micro Program Counter) based on the mpc_mux signal.
        """
        match self.mpc_mux:
            case Signal.SEL_MPC_INC:
                self.mpc += self.inc_value
            case Signal.SEL_MPC_IR:
                self.mpc = self.ir
            case Signal.SEL_MPC_ZERO:
                self.mpc = 0
            case _:
                raise MachineRuntimeError(
                    'invalid mpc signal: ' + self.mpc_mux)

    def get_current_instruction(self):
        """
        Get the current instruction from the instruction memory.

        Returns:
            str: The current instruction string.
        """
        return self.datapath.instruction_memory.read_cell(self.datapath.pc)

    def get_operand(self, index: int) -> int:
        """
        Get the operand at the given index from the operands register.

        Args:
            index (int): The index of the operand (0, 1, or 2).
            0 - rb, 1 - r1, 2 - r2

        Returns:
            int: The operand value.

        Raises:
            MachineRuntimeError: If the index is invalid.
        """
        bin_operands = format(self.operands, '024b')
        if index == 0:
            return int(bin_operands[:4], 2)
        elif index == 1:
            return int(bin_operands[4:8], 2)
        elif index == 2:
            return int(bin_operands[8:], 2)
        else:
            raise MachineRuntimeError('invalid operand index')

    def run_microprogram(self) -> int:
        """
        Run the microprogram for the current MPC (Micro Program Counter) value.

        Returns:
            int: The number of mc executed.
        """
        program = MicroProgramMemory.get_microprogram(self.mpc)
        print(f"Running microprogram: {self.mpc}: {program}")
        for signal in program:
            self._execute_signal(signal)
        self.tick()
        return len(program)

    def _execute_signal(self, signal):
        """
        Execute the given control signal.

        Args:
            signal (Signal): The control signal to be executed.

        Raises:
            StopIteration: If the HALT signal is encountered.
        """
        match signal:
            case Signal.HALT:
                raise StopIteration('HALT')
            case Signal.ALU_ADD | Signal.ALU_SUB | Signal.ALU_MUL | Signal.ALU_AND:
                self.alu.sel_alu(signal)
            case Signal.LATCH_IR:
                self.latch_ir()
            case Signal.LATCH_PC:
                self.datapath.latch_pc()
            case Signal.LATCH_MPC:
                self.latch_mpc()
            case Signal.LATCH_OPERANDS:
                self.latch_operands(self.get_current_instruction())
            case Signal.LATCH_WRITE_MEM:
                self.datapath.data_memory.latch_write_memory()
            case Signal.LATCH_READ_MEM:
                self.datapath.data_memory.latch_read_memory()
            case Signal.SEL_MPC_INC | Signal.SEL_MPC_ZERO | Signal.SEL_MPC_IR:
                self.mpc_mux = signal
            case Signal.SEL_PC_INC | Signal.SEL_PC_ADDR:
                self.datapath.pc_mux = signal
            case Signal.SEL_SRC_ALU | Signal.SEL_SRC_CU | Signal.SEL_SRC_MEM:
                self.datapath.data_src_mux = signal
            case Signal.LATCH_REG:
                self.latch_reg_n()
            case Signal.SEL_REG_L:
                self.sel_left_reg()
            case Signal.SEL_REG_R:
                self.sel_right_reg()
            case Signal.LATCH_REG0 | Signal.LATCH_REG2 | Signal.LATCH_REG3 | \
                    Signal.LATCH_REG4 | Signal.LATCH_REG5 | Signal.LATCH_REG6 | \
                    Signal.LATCH_REG7 | Signal.LATCH_REG8 | Signal.LATCH_REG9 | \
                    Signal.LATCH_REG10 | Signal.LATCH_REG11 | Signal.LATCH_REG12 | \
                    Signal.LATCH_REG13 | Signal.LATCH_REG14 | Signal.LATCH_REG15:
                self.latch_reg_n(signal)
            case Signal.SEL_R_REG0 | Signal.SEL_R_REG2 | Signal.SEL_R_REG3 | \
                    Signal.SEL_R_REG4 | Signal.SEL_R_REG5 | Signal.SEL_R_REG6 | \
                    Signal.SEL_R_REG7 | Signal.SEL_R_REG8 | Signal.SEL_R_REG9 | \
                    Signal.SEL_R_REG10 | Signal.SEL_R_REG11 | Signal.SEL_R_REG12 | \
                    Signal.SEL_R_REG13 | Signal.SEL_R_REG14 | Signal.SEL_R_REG15:
                self.datapath.register_file.sel_right_reg(signal)
            case Signal.SEL_L_REG0 | Signal.SEL_L_REG2 | Signal.SEL_L_REG3 | \
                    Signal.SEL_L_REG4 | Signal.SEL_L_REG5 | Signal.SEL_L_REG6 | \
                    Signal.SEL_L_REG7 | Signal.SEL_L_REG8 | Signal.SEL_L_REG9 | \
                    Signal.SEL_L_REG10 | Signal.SEL_L_REG11 | Signal.SEL_L_REG12 | \
                    Signal.SEL_L_REG13 | Signal.SEL_L_REG14 | Signal.SEL_L_REG15:
                self.datapath.register_file.sel_left_reg(signal)
            case Signal.SEL_ONE_INC:
                self.inc_value = 1
            case Signal.SEL_TWICE_INC_IF_N:
                self.twice_inc_if_n()
            case Signal.SEL_TWICE_INC_IF_Z:
                self.twice_inc_if_z()

    def latch_ir(self):
        self.decode_instruction(
            self.get_current_instruction())

        self.ir = self.decode_line

    def latch_reg_n(self, signal=None):
        if signal:
            index = int(signal) - int(Signal.LATCH_REG0)
        else:
            index = self.get_operand(0)
        self.datapath.register_file.latch_reg_n(
            index, self.datapath.get_register_file_input())

    def sel_left_reg(self):
        if 20 <= self.ir <= 32:
            index = self.get_operand(0)
        else:
            index = self.get_operand(1)
        self.datapath.register_file.sel_left_reg(
            Signal(int(Signal.SEL_L_REG0) + index))

    def sel_right_reg(self):
        if 20 <= self.ir <= 32:
            index = self.get_operand(1)
        else:
            index = self.get_operand(2)
        self.datapath.register_file.sel_right_reg(
            Signal(int(Signal.SEL_R_REG0) + index))

    def twice_inc_if_z(self):
        if self.alu.zero_neg == 0b01:
            self.inc_value = 2
        else:
            self.inc_value = 1

    def twice_inc_if_n(self):
        if self.alu.zero_neg == 0b10:
            self.inc_value = 2
        else:
            self.inc_value = 1
