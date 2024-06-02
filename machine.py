import logging
import sys
from typing import List

from control_unit import ControlUnit
from datapath import DataPath

TICK_LIMIT = 7000000


def read_file(file_name: str) -> List[str]:
    return open(file=file_name, mode='r', encoding='utf-8').read().splitlines()


def prepare(compiled_code: str, compiled_data: str, input_file: str |
            None):
    instructions = read_file(compiled_code)
    data = list(map(lambda x: int(x, 2), read_file(compiled_data)))
    input_str = None if input_file is None else read_file(input_file)[0]
    run_simulation(instructions, data, input_str)


def run_simulation(instructions: List[str], data: List[int], input_str: str | None):
    datapath = DataPath(instructions, data,
                        "" if input_str is None else input_str)
    control_unit = ControlUnit(datapath.alu, datapath)
    instructions_counter = 0
    mc_counter  = 0
    try:
        while control_unit.tick_counter < TICK_LIMIT:
            if control_unit.mpc == 0:
                instructions_counter += 1
            mc_counter += control_unit.run_microprogram()
    except Exception as e:
        print(f"STOP:  {e}")
    print(f"Tick counter:  {control_unit.tick_counter}")
    print(f"Instructions executed: {instructions_counter}")
    print(f"Microprogram counter: {mc_counter}")
    print(f"Output(int): {datapath.io_controller.output_buffer}")
    print(f"Output(str): {list(map(chr, datapath.io_controller.output_buffer))}")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    if len(sys.argv) < 3:
        print("Not enought arguments!")
        print("Usage: python machine.py <compiled_code> <compiled_data> OP(<input_file>)")
        exit(1)

    prepare(sys.argv[1], sys.argv[2], None if len(
        sys.argv) < 4 else sys.argv[3])
