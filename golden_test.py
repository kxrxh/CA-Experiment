import contextlib
import io
import logging
import os
import tempfile

import machine
import pytest
import translator


@pytest.mark.golden_test("golden/*.yml")
def test_translator_and_machine(golden, caplog):
    caplog.set_level(logging.DEBUG)

    with tempfile.TemporaryDirectory() as tmpdirname:
        source = os.path.join(tmpdirname, "source.rasm")
        input_stream = os.path.join(tmpdirname, "input.txt")
        target_code = os.path.join(tmpdirname, "target_code.bin")
        target_data = os.path.join(tmpdirname, "target_dara.bin")

        with open(source, mode="w", encoding="utf-8") as f:
            f.write(golden["in_source"])
        with open(input_stream, mode="w", encoding="utf-8") as f:
            f.write(golden["in_stdin"])

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main(source, target_code, target_data)
            machine.main(target_code, target_data, input_stream)

        with open(target_code, mode="rb") as f:
            code = f.read()
            code = str(code, encoding="utf-8").replace("\r", "")

        with open(target_data, mode="rb") as f:
            data = f.read()
            data = str(data, encoding="utf-8").replace("\r", "")

        assert code == golden.out["out_code"]
        assert stdout.getvalue() == golden.out["out_stdout"]
        assert data == golden.out["out_data"]
        assert caplog.text == golden.out["out_log"]
