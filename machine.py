import logging
import sys
from typing import List


def read_file(file_name: str) -> List[str]:
    return open(file=file_name, mode='r').read().splitlines()


def prepare(compiled_data: str, compiled_code: str, input_file: str |
            None):
    print(read_file(compiled_data))
    print(read_file(compiled_code))
    if input_file is None:
        print("No input file provided!")
    else:
        print(read_file(input_file))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    if len(sys.argv) < 3:
        print("Not enought arguments!")
        print("Usage: python machine.py <compiled_code> <compiled_data> OP(<input_file>)")
        exit(1)

    prepare(sys.argv[1], sys.argv[2], None if len(
        sys.argv) < 4 else sys.argv[3])
