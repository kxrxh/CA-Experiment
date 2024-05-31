from alu import Alu
from datapath import DataPath
from isa import Opcode
from machine_exceptions import MachineRuntimeError
from microcode_new import MicroProgramMemory, Signal


class ControlUnit:
    alu: Alu
    datapath: DataPath

    ir: int  # Instruction register
    operands: int  # Operands (24 bit register)

    mpc_mux: Signal
    mpc: int  # MP counter

    address_out: int
    data_out: int

    tick_counter: int

    def __init__(self, alu: Alu, datapath: DataPath):
        self.ir = 0
        self.operands = 0
        self.mpc = 0
        self.address_out = 0
        self.data_out = 0
        self.alu = alu
        self.datapath = datapath
        self.tick_counter = 0

    def latch_operands(self, instruction: str) -> None:
        self.operands = int(instruction[7:-1], 2)

    def decode_instruction(self, instruction: str) -> None:
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
        }

        self.decode_line = opcode_flag_map[opcode][flag]

    def tick(self):
        self.tick_counter += 1

    def set_address(self, address: int):
        self.address_out = address

    def set_data(self, data: int):
        self.data_out = data

    def latch_mpc(self):
        match self.mpc_mux:
            case Signal.SEL_MPC_INC:
                self.mpc += 1
            case Signal.SEL_MPC_IR:
                self.mpc = self.ir
            case Signal.SEL_MPC_ZERO:
                self.mpc = 0
            case _:
                raise MachineRuntimeError(
                    'invalid mpc signal: ' + self.mpc_mux)

    def get_current_instruction(self):
        return self.datapath.instruction_memory.read_cell(self.datapath.pc)

    def get_operand(self, index: int) -> int:
        if index == 0:
            return self.operands >> 20  # Shift right by 20 bits to extract the first 4 left bits
        elif index == 1:
            # Shift right by 16 bits, then bitwise AND with 1111 to get bits 4 to 7
            return (self.operands >> 16) & 0b1111
        elif index == 2:
            # Bitwise AND with 16 bits set to 1 to get the last 16 bits
            return self.operands & 0xFFFF
        else:
            raise MachineRuntimeError('invalid operand index')

    def run_microprogram(self):  # noqa: C901
        program = MicroProgramMemory.get_microprogram(self.mpc)
        for signal in program:
            match signal:
                case Signal.HALT:
                    raise StopIteration('HALT')
                case Signal.ALU_ADD | Signal.ALU_SUB | Signal.ALU_MUL | Signal.AND:
                    self.alu.sel_alu(signal)
                case Signal.LATCH_IR:
                    self.datapath.control_unit.ir = self.decode_instruction(
                        self.get_current_instruction())
                case Signal.LATCH_PC:
                    self.datapath.latch_pc()
                case Signal.LATCH_MPC:
                    self.latch_mpc()
                case Signal.LATCH_OPERANDS:
                    self.datapath.operands = self.latch_operands(
                        self.get_current_instruction())
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
                    index = self.get_operand(0)
                    self.datapath.register_file.latch_reg_n(
                        index, self.datapath.get_register_file_input())
                case Signal.LATCH_REG0 | Signal.LATCH_REG2 | Signal.LATCH_REG3 | \
                        Signal.LATCH_REG4 | Signal.LATCH_REG5 | Signal.LATCH_REG6 | \
                        Signal.LATCH_REG7 | Signal.LATCH_REG8 | Signal.LATCH_REG9 | \
                        Signal.LATCH_REG10 | Signal.LATCH_REG11 | Signal.LATCH_REG12 | \
                        Signal.LATCH_REG13 | Signal.LATCH_REG14 | Signal.LATCH_REG15:
                    index = int(signal) - int(Signal.LATCH_REG0)
                    self.datapath.register_file.latch_reg_n(
                        index, self.datapath.get_register_file_input())
                case Signal.SEL_REG_L:
                    index = self.get_operand(1)
                    self.datapath.register_file.sel_left_reg(
                        Signal(int(Signal.SEL_REG0) + index))
                case Signal.SEL_REG_R:
                    index = self.get_operand(2)
                    self.datapath.register_file.sel_right_reg(
                        Signal(int(Signal.LATCH_REG0) + index))
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
