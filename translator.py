import re
import sys
from typing import Dict, List, Tuple
from isa import DATA_MEMORY_BEGIN_ADDRESS, INSTRUCTION_MEMORY_BEGIN_ADDRESS, Opcode, INPUT_CELL_ADDRESS, OUTPUT_CELL_ADDRESS
from translator_excpetions import InvalidArgumentError, TranslatorError
from type_token import Token, TokenType

# Regular expressions for different types of tokens
REGISTER_REGEX = re.compile(r'\b(r\d+)\b')
LABEL_REGEX = re.compile(r'[a-zA-Z_]\w*:')
NUMBER_REGEX = re.compile(r'#\b\d+\b')
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
        if not line:
            continue
        code_lines.append(line)
    return code_lines


def replace_quoted_strings(line: str) -> Tuple[str, dict]:
    string_placeholders = {}
    placeholder_index = 0
    matches = list(re.finditer(STRING_REGEX, line))
    for match in matches:
        placeholder = f"__STRING_PLACEHOLDER_{placeholder_index}__"
        string_placeholders[placeholder] = match.group(
            0).replace("\"", "").replace("\\0", chr(0))
        line = line.replace(match.group(0), placeholder, 1)
        placeholder_index += 1
    return line, string_placeholders


def process_token(token: str, string_placeholders: dict, tokens: List[Token]):
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
                    current_address += len(
                        token.get_string_value().strip('"').replace('\\0', ''))
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


def convert_math_command_to_binary(opcode: int, tokens: List[Token], data_labels: Dict[str, int]) -> str:
    if len(tokens) != 3:
        raise TranslatorError("Invalid arguments count: expected 3")
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


def convert_branch_command_to_binary(opcode: int, tokens: List[Token], text_label: dict[str, int]) -> str:
    if len(tokens) not in [1, 3]:
        raise TranslatorError(
            "Invalid arguments for branch command: expected 3 or 1")

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

    return create_binary_command(opcode, rb.get_int_value(), r1.get_int_value(), text_label[r2.get_string_value()], 0)


def convert_memory_command_to_binary(opcode: int, tokens: List[Token], data_labels: Dict[str, int]) -> str:
    if len(tokens) != 2:
        raise TranslatorError("Invalid arguments count: expected 2")

    # Read destination register argument
    rb = tokens[0]
    if rb.get_type() != TokenType.REGISTER:
        raise InvalidArgumentError("rb", ["register"])

    # Read address argument
    arg = tokens[1]
    if arg.get_type() not in [TokenType.LABEL, TokenType.REGISTER]:
        raise InvalidArgumentError("arg", ["label", "register"])

    r1 = r2 = 0

    # Set R1 if opcode is LOAD_WORD, otherwise set R2
    if Opcode.LOAD_WORD.code == opcode:
        r1 = arg.get_int_value()
        flag = 0
    else:
        r2 = data_labels[arg.get_string_value()]
        flag = 1
    return create_binary_command(opcode, rb.get_int_value(), r1, r2, flag)


def convert_no_args_command_to_binary(opcode: int) -> str:
    return create_binary_command(opcode, 0, 0, 0, 0)


def convert_tokens_to_binary(tokens: List[Token], data_labels: Dict[str, int], text_label: Dict[str, int]) -> str:
    if len(tokens) == 0:
        raise TranslatorError('No tokens provided')

    for i, token in enumerate(tokens):
        if token.get_type() == TokenType.INSTRUCTION:
            opcode = Opcode.get_opcode_by_mnemonic(token.get_string_value())
            if opcode.is_mathlog():
                return convert_math_command_to_binary(opcode.get_code(), tokens[i+1:], data_labels)
            elif opcode.is_branch():
                return convert_branch_command_to_binary(opcode.get_code(), tokens[i+1:], text_label)
            elif opcode.is_no_args():
                return convert_no_args_command_to_binary(opcode.get_code())
            elif opcode.is_memory():
                return convert_memory_command_to_binary(opcode.get_code(), tokens[i+1:], data_labels)
    return ""


def convert_data_tokens_to_binary(tokens: List[Token]) -> List[str]:
    if len(tokens) == 0:
        raise TranslatorError('No tokens provided')
    result = []
    for token in tokens:
        if token.get_type() == TokenType.NUMBER:
            result.append(f"{token.get_int_value():016b}")
        elif token.get_type() == TokenType.STRING:
            for char in token.get_string_value():
                result.append(f"{ord(char):032b}")
    return result


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Please provide a input_file')
        print('Usage: python translator.py <input_file> <code_output> <data_output>')
        sys.exit(1)

    file_name = sys.argv[1]
    file_code_output = sys.argv[2]
    file_data_output = sys.argv[3]
    code = read_file(file_name)
    tokenized = tokenize(code)

    data_label_mapping = get_data_labels_mapping(tokenized)
    text_label_mapping = get_text_labels_mapping(tokenized)

    output = []

    print("-- Text section --")
    for i, token in enumerate(tokenized):
        binary = convert_tokens_to_binary(
            token, data_label_mapping, text_label_mapping)
        if binary:
            print(f"{binary} {code[i]}")
            output.append(binary)
    write_file(file_code_output, output)

    print("-- Data section --")
    data_output = []
    for token_line in get_data_section(tokenized):
        converted = convert_data_tokens_to_binary(token_line)
        for line in converted:
            print(line, chr(int(line, 2)))
            data_output.append(line)
    write_file(file_data_output, data_output)
