from typing import List
from type import Token, TokenType

INSTRUCTION_SET = {'hlt': {'opcode': 0x00, 'operands': 0},
                   'add': {'opcode': 0x01, 'operands': 3},
                   'mul': {'opcode': 0x02, 'operands': 3},
                   'sub': {'opcode': 0x03, 'operands': 3},
                   'div': {'opcode': 0x04, 'operands': 3},
                   'mod': {'opcode': 0x05, 'operands': 3},
                   'and': {'opcode': 0x06, 'operands': 3},
                   'or': {'opcode': 0x07, 'operands': 3},
                   'xor': {'opcode': 0x08, 'operands': 3},
                   'jmp': {'opcode': 0x0A, 'operands': 1},
                   'ret': {'opcode': 0x0B, 'operands': 0},
                   'mov': {'opcode': 0x0C, 'operands': 2},
                   }


class ParsingError(Exception):
    def __init__(self, message: str):
        self.message = message


def encode_instuction(tokens: List[Token]) -> int:
    for i, token in enumerate(tokens):
        if token.type == TokenType.INSTRUCTION:
            try:
                instruction_info = INSTRUCTION_SET[token.get_value().lower()]
            except KeyError:
                raise ParsingError(
                    'Unknown instruction. Invalid instruction: ' + token.get_value())

            if len(tokens) - (i + 1) != instruction_info['operands']:
                raise ParsingError(f'Invalid number of operands!. For instruction: {
                                   token.get_value()} expected: {instruction_info["operands"]}, got: {len(tokens) - (i + 1)}')

            binary_code = instruction_info['opcode'] << 24

            for i, operand_token in enumerate(tokens[i+1:]):
                opreand_value = 0
                if operand_token.get_type() == TokenType.REGISTER:
                    register_index = int(operand_token.get_value()[1:])
                    if register_index > 15:
                        raise ParsingError(f'Invalid register value!. For instruction: {
                                           token.get_value()}')
                    opreand_value = register_index
                    # Encode as register operand
                    opreand_value = (0 << 6) | opreand_value
                elif operand_token.get_type() == TokenType.NUMBER:
                    opreand_value = int(operand_token.get_value())
                    # Encode as immediate operand
                    opreand_value = (1 << 6) | opreand_value
                elif operand_token.get_type() == TokenType.LABEL:
                    pass
                else:
                    # Todo: add label operand support
                    raise ParsingError(
                        f'Invalid operand type!. For instruction: {token.get_value()}')

                # Shift operand value to its position in binary code
                binary_code |= (opreand_value << 16 - i * 8)

            return binary_code
        return -1
