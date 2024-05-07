from enum import Enum
import re
import sys
from typing import List
from encoder import encode_instuction
from type import Token, TokenType

# Regular expressions for different types of tokens
REGISTER_REGEX = re.compile(r'\b(x\d+)\b')
LABEL_REGEX = re.compile(r'[a-zA-Z_]\w*:')
NUMBER_REGEX = re.compile(r'\b\d+\b')
COMMENT_REGEX = re.compile(r'//.*')
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


def tokenize_line(line) -> List[Token]:
    """Tokenize a single line of code."""
    tokens: List[Token] = []
    for token in re.split(r'[\s,]+', line):
        if token:
            if re.match(REGISTER_REGEX, token):
                tokens.append(Token(TokenType.REGISTER, token))
            elif re.match(LABEL_REGEX, token):
                # Remove the :
                tokens.append(Token(TokenType.LABEL, token[:-1]))
            elif re.match(NUMBER_REGEX, token):
                tokens.append(Token(TokenType.NUMBER, int(token)))
            elif re.match(SECTION_REGEX, token):
                # Remove the .
                tokens.append(Token(TokenType.SECTION, token[1:]))
            else:
                if any([t.get_type() == TokenType.INSTRUCTION for t in tokens]):
                    tokens.append(Token(TokenType.LABEL, token))
                else:
                    tokens.append(Token(TokenType.INSTRUCTION, token))
    return tokens


def tokenize(code: List[str]) -> List[List[Token]]:
    """Tokenize a list of code lines."""
    return [tokenize_line(line) for line in code]


# def assemble(tokens: List[List[Token]]) -> str:
#     section = {}
#     current_section = None
#     for tokens_line in tokens:
#         if tokens_line[0].get_type() == TokenType.SECTION:
#             current_section = tokens_line[0].get_value()
#             section[current_section] = []
#         elif current_section:
#             instruction_tokens = []
#             for token in tokens_line:
#                 if token.get_type() == TokenType.INSTRUCTION:
#                     //


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please provide a filename')
        print('Usage: python translator.py <filename>')
        sys.exit(1)

    file_name = sys.argv[1]
    code = read_file(file_name)
    tokenized = tokenize(code)
    for tokens in tokenized:
        for token in tokens:
            print(token)
        print(encode_instuction(tokens))
        print(bin(encode_instuction(tokens)))
        print()
