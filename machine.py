from __future__ import annotations

import logging
import sys

from control_unit import ControlUnit
from datapath import DataPath

TICK_LIMIT = 7000


def read_file(file_name: str) -> list[str]:
    return open(file=file_name, encoding="utf-8").read().splitlines()


def main(compiled_code: str, compiled_data: str, input_file: str | None):
    instructions = read_file(compiled_code)
    data = list(map(lambda x: int(x, 2), read_file(compiled_data)))
    input_str = None
    if input_file is not None:
        input_data = read_file(input_file)
        if len(input_data) != 0:
            input_str = input_data[0]
    run_simulation(instructions, data, input_str)


def run_simulation(instructions: list[str], data: list[int], input_str: str | None):
    datapath = DataPath(instructions, data, "" if input_str is None else input_str)
    control_unit = ControlUnit(datapath.alu, datapath)
    instructions_counter = 0
    mc_counter = 0
    try:
        while control_unit.tick_counter < TICK_LIMIT:
            if control_unit.mpc == 0:
                instructions_counter += 1
            mc_counter += control_unit.run_microprogram()
            logging.debug(
                f"Machine state: IR({control_unit.ir}), MPC({control_unit.mpc}), PC({datapath.pc}), REGISTERS({
                    datapath.register_file.registers}), NZ({datapath.alu.neg_zero}), TICKS({control_unit.tick_counter}), MC_COUNTER({mc_counter})"
            )
    except Exception as e:
        logging.debug(f"StopIteration reason:  {e}")
    logging.debug(f"LOC: {len(instructions)}")
    logging.debug(f"Ticks:  {control_unit.tick_counter}")
    logging.debug(f"Instructions executed: {instructions_counter}")
    logging.debug(f"Microprogram executed: {mc_counter}")
    logging.debug(f"Output(int): {datapath.io_controller.output_buffer}")
    logging.debug(
        f"Output(str): {list(map(lambda x: chr(x) if x in range(
            0x110000) else "NONE", datapath.io_controller.output_buffer))}"
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    assert (
        len(sys.argv) >= 3
    ), "Not enought arguments! Usage: python machine.py <compiled_code> <compiled_data> OP(<input_file>)"
    main(sys.argv[1], sys.argv[2], None if len(sys.argv) < 4 else sys.argv[3])
