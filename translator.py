from __future__ import annotations

import re
import sys

from isa import (
    DATA_MEMORY_BEGIN_ADDRESS,
    INPUT_CELL_ADDRESS,
    INSTRUCTION_MEMORY_BEGIN_ADDRESS,
    OUTPUT_CELL_ADDRESS,
    Opcode,
)
from translator_excpetions import InvalidArgumentCountError, InvalidArgumentError, NoTokenError
from translator_token import Token, TokenType

# Regular expressions for different types of tokens
REGISTER_REGEX = re.compile(r"\b(r\d+)\b")
LABEL_REGEX = re.compile(r"[a-zA-Z_]\w*:")
NUMBER_REGEX = re.compile(r"#\b\d+\b")
COMMENT_REGEX = re.compile(r"//.*")
STRING_REGEX = re.compile(r'"[^\"]*"')
SECTION_REGEX = re.compile(r"\.(\w+)")


def remove_comments(text: str) -> str:
    """
    Remove comments from the given text
    """
    return re.sub(COMMENT_REGEX, "", text)


def write_file(filename: str, code: list[str]):
    open(filename, "w").write("\n".join(code))


def read_file(filename: str) -> list[str]:
    """Read the contents of a file and return them as a list of lines."""
    file = open(filename)
    code_lines: list[str] = []
    for line in file:
        line = remove_comments(line).strip()
        if not line:
            continue
        code_lines.append(line)
    return code_lines


def replace_quoted_strings(line: str) -> tuple[str, dict]:
    string_placeholders = {}
    placeholder_index = 0
    matches = list(re.finditer(STRING_REGEX, line))
    for match in matches:
        placeholder = f"__STRING_PLACEHOLDER_{placeholder_index}__"
        string_placeholders[placeholder] = match.group(0).replace('"', "").replace("\\0", chr(0))
        line = line.replace(match.group(0), placeholder, 1)
        placeholder_index += 1
    return line, string_placeholders


def process_token(token: str, string_placeholders: dict, tokens: list[Token]):
    if token in string_placeholders:
        tokens.append(Token(TokenType.STRING, string_placeholders[token]))
    elif re.match(REGISTER_REGEX, token):
        tokens.append(Token(TokenType.REGISTER, token[1:]))
    elif re.match(LABEL_REGEX, token):
        tokens.append(Token(TokenType.LABEL, token[:-1]))
    elif re.match(NUMBER_REGEX, token):
        tokens.append(Token(TokenType.NUMBER, int(token[1:])))
    elif re.match(SECTION_REGEX, token):
        tokens.append(Token(TokenType.SECTION, token[1:]))
    else:
        if any([t.type == TokenType.INSTRUCTION for t in tokens]):
            tokens.append(Token(TokenType.LABEL, token))
        else:
            tokens.append(Token(TokenType.INSTRUCTION, token))


def tokenize_line(line) -> list[Token]:
    """Tokenize a single line of code."""
    tokens: list[Token] = []

    line, string_placeholders = replace_quoted_strings(line)

    for token in re.split(r"[\s,]+", line):
        if token:
            process_token(token, string_placeholders, tokens)

    return tokens


def tokenize(code: list[str]) -> list[list[Token]]:
    """Tokenize a list of code lines."""
    result = []
    for line in code:
        tokenized = tokenize_line(line)
        if len(tokenized) > 0:
            result.append(tokenized)
    return result


def get_data_section(token_line: list[list[Token]]) -> list[list[Token]]:
    """Get the data section from the given tokens."""
    data_section_lines = []
    is_data_section = False
    for line in token_line:
        if line[0].get_type() == TokenType.SECTION:
            if line[0].get_value() == "data":
                is_data_section = True
            else:
                is_data_section = False
            continue
        if is_data_section:
            data_section_lines.append(line)

    return data_section_lines


def get_text_section(token_line: list[list[Token]]) -> list[list[Token]]:
    text_section_lines = []
    is_text_section = False
    for line in token_line:
        if line[0].get_type() == TokenType.SECTION:
            if line[0].get_value() == "text":
                is_text_section = True
            else:
                is_text_section = False
            continue
        if is_text_section:
            text_section_lines.append(line)

    return text_section_lines


def get_all_labels(token_line: list[list[Token]]) -> list[Token]:
    """Get all labels from the given tokenized lines."""
    labels = []
    for line in token_line:
        if line[0].get_type() == TokenType.LABEL:
            labels.append(line[0])
    return labels


def get_data_labels_mapping(token_lines: list[list[Token]]) -> dict[str, int]:
    mapping = {"in": INPUT_CELL_ADDRESS, "out": OUTPUT_CELL_ADDRESS}
    current_address = DATA_MEMORY_BEGIN_ADDRESS

    data_section_lines = get_data_section(token_lines)
    for line in data_section_lines:
        if line[0].get_type() == TokenType.LABEL:
            label = line[0].get_string_value()
            # Calculate the memory address for this label
            mapping[label] = current_address
            # Assume the next token in the line is a string
            for token in line[1:]:
                if token.get_type() == TokenType.STRING:
                    # Increment the current_address by the length of the string
                    current_address += len(token.get_string_value().strip('"').replace("\\0", ""))
                elif token.get_type() in [TokenType.NUMBER, TokenType.LABEL]:
                    current_address += 1
    print(mapping)
    return mapping


def get_text_labels_mapping(token_lines: list[list[Token]]) -> dict[str, int]:
    mapping = {}
    instruction_index = INSTRUCTION_MEMORY_BEGIN_ADDRESS

    text_section_lines = get_text_section(token_lines)
    for _, line in enumerate(text_section_lines):
        if not line:
            continue
        if line[0].get_type() == TokenType.LABEL:
            label = line[0].get_string_value()
            mapping[label] = instruction_index
            if len(line) == 1:
                instruction_index -= 1
        instruction_index += 1
    print(mapping)
    return mapping


def create_binary_command(opcode: int, rb: int, arg1: int, arg2: int, flag: int) -> str:
    # Ensure each argument fits within its designated size
    opcode = opcode & 0b1111111  # 7 bits for opcode
    rb = rb & 0b1111  # 4 bits for rb
    arg1 = arg1 & 0b1111  # 4 bits for arg1
    arg2 = arg2 & 0b1111111111111111  # 16 bits for arg2
    flag = flag & 0b1  # 1 bit for flag

    return f"{opcode:07b}{rb:04b}{arg1:04b}{arg2:016b}{flag:01b}"


def convert_math_command_to_binary(opcode: int, tokens: list[Token], data_labels: dict[str, int]) -> str:
    if len(tokens) != 3:
        raise InvalidArgumentCountError([3])
    rb = tokens[0]
    if rb.get_type() != TokenType.REGISTER:
        raise InvalidArgumentError("rb", ["register"])
    r1 = tokens[1]
    if r1.get_type() != TokenType.REGISTER:
        raise InvalidArgumentError("r1", ["register"])
    r2 = tokens[2]
    if r2.get_type() not in [TokenType.REGISTER, TokenType.NUMBER, TokenType.LABEL]:
        raise InvalidArgumentError("r2", ["register", "number", "label"])

    sub_flag = 1

    rb_value = rb.get_int_value()
    r1_value = r1.get_int_value()

    # Label is represented as a number. P.S. Address as a number
    if r2.get_type() == TokenType.LABEL:
        r2_value = data_labels[r2.get_string_value()]
    elif r2.get_type() == TokenType.REGISTER:
        sub_flag = 0
        r2_value = r2.get_int_value()
    else:
        r2_value = r2.get_int_value()

    return create_binary_command(opcode, rb_value, r1_value, r2_value, sub_flag)


def convert_branch_command_to_binary(opcode: int, tokens: list[Token], text_label: dict[str, int]) -> str:
    if len(tokens) not in [1, 3]:
        raise InvalidArgumentCountError([1, 3])

    rb = tokens[0]

    if len(tokens) == 1:
        # Jump instruction:
        if rb.get_type() != TokenType.LABEL:
            raise InvalidArgumentError("rb", ["label"])
        return create_binary_command(opcode, 0, 0, text_label[rb.get_string_value()], 1)

    if rb.get_type() != TokenType.REGISTER:
        raise InvalidArgumentError("rb", ["register"])
    r1 = tokens[1]
    if r1.get_type() != TokenType.REGISTER:
        raise InvalidArgumentError("r1", ["register"])

    r2 = tokens[2]
    if r2.get_type() != TokenType.LABEL:
        raise InvalidArgumentError("rb", ["label"])

    return create_binary_command(
        opcode,
        rb.get_int_value(),
        r1.get_int_value(),
        text_label[r2.get_string_value()],
        0,
    )


def convert_memory_command_to_binary(opcode: int, tokens: list[Token]) -> str:
    if len(tokens) != 2:
        raise InvalidArgumentCountError([2])

    # Read destination register argument
    rb_t = tokens[0]
    if rb_t.get_type() != TokenType.REGISTER:
        raise InvalidArgumentError("rb", ["register"])

    # Read address argument
    arg = tokens[1]
    if arg.get_type() not in [TokenType.LABEL, TokenType.REGISTER]:
        raise InvalidArgumentError("arg", ["label", "register"])

    rb = rb_t.get_int_value()  # Data
    r1 = arg.get_int_value()  # Address
    r2 = 0
    # Set R1 if opcode is LOAD_WORD, otherwise set R2
    if Opcode.LOAD_WORD.code == opcode:
        flag = 0
    else:
        r2 = rb
        rb = 0
        flag = 1
    return create_binary_command(opcode, rb, r1, r2, flag)


def convert_no_args_command_to_binary(opcode: int) -> str:
    return create_binary_command(opcode, 0, 0, 0, 0)


def _find_first_instruction(tokens: list[Token]) -> int:
    for i, token in enumerate(tokens):
        if token.get_type() == TokenType.INSTRUCTION:
            return i
    return -1


def convert_tokens_to_binary(tokens: list[Token], data_labels: dict[str, int], text_label: dict[str, int]) -> str:
    if len(tokens) == 0:
        raise NoTokenError()

    i = _find_first_instruction(tokens)
    if i < 0:
        return ""
    token = tokens[i]

    opcode = Opcode.get_opcode_by_mnemonic(token.get_string_value())
    if opcode.is_mathlog():
        return convert_math_command_to_binary(opcode.get_code(), tokens[i + 1 :], data_labels)
    if opcode.is_branch():
        return convert_branch_command_to_binary(opcode.get_code(), tokens[i + 1 :], text_label)
    if opcode.is_no_args():
        return convert_no_args_command_to_binary(opcode.get_code())
    if opcode.is_memory():
        return convert_memory_command_to_binary(opcode.get_code(), tokens[i + 1 :])
    return ""


def convert_data_tokens_to_binary(tokens: list[Token]) -> list[str]:
    if len(tokens) == 0:
        raise NoTokenError()
    result = []
    for token in tokens:
        if token.get_type() == TokenType.NUMBER:
            result.append(f"{token.get_int_value():032b}")
        elif token.get_type() == TokenType.STRING:
            for char in token.get_string_value():
                result.append(f"{ord(char):032b}")
    return result


def main(source: str, target_code: str, target_data: str):
    code = read_file(source)
    tokenized = tokenize(code)

    data_label_mapping = get_data_labels_mapping(tokenized)
    text_label_mapping = get_text_labels_mapping(tokenized)

    output = []

    print("-- Text section --")
    instruction_mem_counter = 1
    for i, token in enumerate(tokenized):
        binary = convert_tokens_to_binary(token, data_label_mapping, text_label_mapping)
        if binary:
            print(f"{instruction_mem_counter} {binary} {code[i]}")
            output.append(binary)
            instruction_mem_counter += 1
    write_file(target_code, output)

    print("-- Data section --")
    data_output = []
    data_mem_counter = 2
    for token_line in get_data_section(tokenized):
        converted = convert_data_tokens_to_binary(token_line)
        for line in converted:
            data_output.append(line)
            print(f"{data_mem_counter}  {line}")
            data_mem_counter += 1
    write_file(target_data, data_output)


if __name__ == "__main__":
    assert len(sys.argv) == 4, "Usage: python translator.py  <input_file>  <code_output>  <data_output>"

    source = sys.argv[1]
    file_code_output = sys.argv[2]
    file_data_output = sys.argv[3]

    main(source, file_code_output, file_data_output)
