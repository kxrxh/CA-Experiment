import re
import sys
from typing import Dict, List, Tuple
from isa import DATA_MEMORY_BEGIN_ADDRESS, INSTRUCTION_MEMORY_BEGIN_ADDRESS, Opcode, INPUT_CELL_ADDRESS, OUTPUT_CELL_ADDRESS
from type_token import Token, TokenType

# Regular expressions for different types of tokens
REGISTER_REGEX = re.compile(r'\b(r\d+)\b')
LABEL_REGEX = re.compile(r'[a-zA-Z_]\w*:')
NUMBER_REGEX = re.compile(r'\b\d+\b')
COMMENT_REGEX = re.compile(r'//.*')
STRING_REGEX = re.compile(r'"[^\"]*"')
SECTION_REGEX = re.compile(r'\.(\w+)')


def remove_comments(text: str) -> str:
    """
    Remove comments from the given text
    """
    return re.sub(COMMENT_REGEX, '', text)


def write_file(filename: str, code: List[str]):
    open(filename, 'w').write('\n'.join(code))


def read_file(filename: str) -> List[str]:
    """Read the contents of a file and return them as a list of lines."""
    file = open(filename, 'r')
    code_lines: List[str] = []
    for line in file:
        line = remove_comments(line).strip()
        code_lines.append(line)
    return code_lines


def replace_quoted_strings(line: str) -> Tuple[str, dict]:
    string_placeholders = {}
    placeholder_index = 0
    matches = list(re.finditer(STRING_REGEX, line))
    for match in matches:
        placeholder = f"__STRING_PLACEHOLDER_{placeholder_index}__"
        string_placeholders[placeholder] = match.group(0)
        line = line.replace(match.group(0), placeholder, 1)
        placeholder_index += 1
    return line, string_placeholders


def process_token(token: str, string_placeholders: dict, tokens: List[Token]):
    if token in string_placeholders:
        tokens.append(Token(TokenType.STRING, string_placeholders[token]))
    elif re.match(REGISTER_REGEX, token):
        tokens.append(Token(TokenType.REGISTER, token))
    elif re.match(LABEL_REGEX, token):
        tokens.append(Token(TokenType.LABEL, token[:-1]))
    elif re.match(NUMBER_REGEX, token):
        tokens.append(Token(TokenType.NUMBER, int(token)))
    elif re.match(SECTION_REGEX, token):
        tokens.append(Token(TokenType.SECTION, token[1:]))
    else:
        if any([t.type == TokenType.INSTRUCTION for t in tokens]):
            tokens.append(Token(TokenType.LABEL, token))
        else:
            tokens.append(Token(TokenType.INSTRUCTION, token))


def tokenize_line(line) -> List[Token]:
    """Tokenize a single line of code."""
    tokens: List[Token] = []

    line, string_placeholders = replace_quoted_strings(line)

    for token in re.split(r'[\s,]+', line):
        if token:
            process_token(token, string_placeholders, tokens)

    return tokens


def tokenize(code: List[str]) -> List[List[Token]]:
    """Tokenize a list of code lines."""
    result = []
    for line in code:
        tokenized = tokenize_line(line)
        if len(tokenized) > 0:
            result.append(tokenized)
    return result


def get_data_section(token_line: List[List[Token]]) -> List[List[Token]]:
    """Get the data section from the given tokens."""
    data_section_lines = []
    is_data_section = False
    for line in token_line:
        if line[0].get_type() == TokenType.SECTION:
            if line[0].get_value() == 'data':
                is_data_section = True
            else:
                is_data_section = False
            continue
        if is_data_section:
            data_section_lines.append(line)

    return data_section_lines


def get_text_section(token_line: List[List[Token]]) -> List[List[Token]]:
    text_section_lines = []
    is_text_section = False
    for line in token_line:
        if line[0].get_type() == TokenType.SECTION:
            if line[0].get_value() == 'text':
                is_text_section = True
            else:
                is_text_section = False
            continue
        if is_text_section:
            text_section_lines.append(line)

    return text_section_lines


def get_all_labels(token_line: List[List[Token]]) -> List[Token]:
    """Get all labels from the given tokenized lines."""
    labels = []
    for line in token_line:
        if line[0].get_type() == TokenType.LABEL:
            labels.append(line[0])
    return labels


def get_data_labels_mapping(token_lines: List[List[Token]]) -> Dict[str, int]:
    mapping = {'in': INPUT_CELL_ADDRESS, 'out': OUTPUT_CELL_ADDRESS}
    current_address = DATA_MEMORY_BEGIN_ADDRESS

    data_section_lines = get_data_section(token_lines)
    for line in data_section_lines:
        if line[0].get_type() == TokenType.LABEL:
            label = line[0].get_string_value()
            # Calculate the memory address for this label
            mapping[label] = current_address
            # Assume the next token in the line is a string
            for token in line:
                if token.get_type() == TokenType.STRING:
                    # Increment the current_address by the length of the string
                    current_address += len(token.get_string_value().strip('"').replace('\\0', ''))
                elif token.get_type() in [TokenType.NUMBER, TokenType.LABEL]:
                    current_address += 1
    print(mapping)
    return mapping


def get_text_labels_mapping(token_lines: List[List[Token]]) -> Dict[str, int]:
    mapping = {}
    instruction_index = INSTRUCTION_MEMORY_BEGIN_ADDRESS

    text_section_lines = get_text_section(token_lines)
    for index, line in enumerate(text_section_lines):
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
    return f"{opcode:07b}{rb:04b}{arg1:04b}{arg2:016b}{flag:01b}"


def convert_math_command_to_binary(opcode: int, tokens: List[Token]) -> str:
    if len(tokens) != 3:
        raise RuntimeError("Invalid arguments count: expected 3")
    rb = tokens[0]
    if rb.get_type() != TokenType.REGISTER:
        raise RuntimeError("Invalid arguments: rb should be register")
    r1 = tokens[1]
    if r1.get_type() != TokenType.REGISTER:
        raise RuntimeError("Invalid arguments: r1 should be register")
    r2 = tokens[2]
    if r2.get_type() not in [TokenType.REGISTER, TokenType.NUMBER]:
        raise RuntimeError(
            "Invalid arguments: r2 should be register or number")
    f = 1

    r1_value = r1.get_string_value()
    r2_value = r2.get_string_value()
    rb_value = rb.get_string_value()
    if r2_value.startswith('r'):
        f = 0
        r2_value = r2_value[1:]
    return create_binary_command(opcode, int(rb_value[1:]), int(r1_value[1:]), int(r2_value), f)


def convert_branch_command_to_binary(opcode: int, tokens: List[Token], text_label: dict[str, int]) -> str:
    if len(tokens) not in [3, 1]:
        raise RuntimeError(
            "Invalid arguments for branch command: expected 3 or 1")

    rb = tokens[0]
    if len(tokens) == 1:
        if rb.get_type() != TokenType.LABEL:
            raise RuntimeError("Invalid arguments: r2 should be label")
        return create_binary_command(opcode, 0, 0, int(rb.get_string_value()), 1)
    if rb.get_type() != TokenType.REGISTER:
        raise RuntimeError("Invalid arguments: rb should be register")
    r1 = tokens[1]
    if r1.get_type() != TokenType.REGISTER:
        raise RuntimeError("Invalid arguments: r1 should be register")

    r2 = tokens[2]
    if r2.get_type() != TokenType.LABEL:
        raise RuntimeError("Invalid arguments: r2 should be label")

    return create_binary_command(opcode, int(rb.get_string_value()[1:]), int(r1.get_string_value()[1:]), text_label[r2.get_string_value()], 0)


def convert_load_command_to_binary(opcode: int, tokens: List[Token], data_labels: Dict[str, int]) -> str:
    if len(tokens) != 2:
        raise RuntimeError("Invalid arguments count: expected 2")

    # Read destination register argument
    rb = tokens[0]
    if rb.get_type() != TokenType.REGISTER:
        raise RuntimeError("Invalid arguments: rb should be register")

    # Read address argument
    r2 = tokens[1]
    if r2.get_type() != TokenType.LABEL:
        raise RuntimeError("Invalid arguments: r1 should be register")
    # Set flag to 0 if opcode is load, otherwise set it to 1
    flag = 0 if opcode == Opcode.LOAD.value else 1
    return create_binary_command(opcode, int(rb.get_string_value()[1:]), 0, data_labels[r2.get_string_value()], flag)


def convert_no_args_command_to_binary(opcode: int) -> str:
    return create_binary_command(opcode, 0, 0, 0, 0)


def convert_tokens_to_binary(tokens: List[Token], data_labels: Dict[str, int], text_label: Dict[str, int]) -> str:
    if len(tokens) == 0:
        raise ValueError('Token line is empty')

    for i, token in enumerate(tokens):
        if token.get_type() == TokenType.INSTRUCTION:
            opcode = Opcode.get_opcode_by_mnemonic(token.get_string_value())
            if opcode.is_math():
                return convert_math_command_to_binary(opcode.get_code(), tokens[i+1:])
            elif opcode.is_branch():
                return convert_branch_command_to_binary(opcode.get_code(), tokens[i+1:], text_label)
            elif opcode.is_no_args():
                return convert_no_args_command_to_binary(opcode.get_code())
            elif opcode.is_load():
                return convert_load_command_to_binary(opcode.get_code(), tokens[i+1:], data_labels)
    return ""


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Please provide a filename')
        print('Usage: python translator.py <filename> <code_output> <data_output>')
        sys.exit(1)

    file_name = sys.argv[1]
    file_code_output = sys.argv[2]
    file_data_output = sys.argv[3]
    code = read_file(file_name)
    tokenized = tokenize(code)

    data_label_mapping = get_data_labels_mapping(tokenized)
    text_label_mapping = get_text_labels_mapping(tokenized)

    output = []
    for i, token in enumerate(tokenized):
        binary = convert_tokens_to_binary(token, data_label_mapping, text_label_mapping)
        if binary!= "":
            output.append(binary)
    write_file(file_code_output, output)
