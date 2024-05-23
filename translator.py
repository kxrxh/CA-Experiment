import re
import sys
from typing import List, Tuple
from isa import Opcode
from type import Token, TokenType

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


def get_all_labels(token_line: List[List[Token]]) -> List[Token]:
    """Get all labels from the given tokenized lines."""
    labels = []
    for line in token_line:
        if line[0].get_type() == TokenType.LABEL:
            labels.append(line[0])
    return labels


def tokens_to_binary(tokens: List[Token]) -> str:
    opcode: int = -1

    for token in tokens:
        if token.get_type() == TokenType.INSTRUCTION:
            opcode = Opcode.str_to_opcode(token.get_value())
    if opcode < 0:
        return ""


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please provide a filename')
        print('Usage: python translator.py <filename>')
        sys.exit(1)

    file_name = sys.argv[1]
    code = read_file(file_name)
    tokenized = tokenize(code)

    for l in (tokenized):
        tokens_to_binary(l)
        for t in l:
            print(t)
        print()
