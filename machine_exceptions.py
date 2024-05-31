
class StopIteration(Exception):
    def __init__(self, msg):
        super().__init__(f"StopIteration: {msg}")


class MachineRuntimeError(StopIteration):
    def __init__(self, msg):
        super().__init__(f"runtime error[{msg}]")


class InvalidRegisterIndex(MachineRuntimeError):
    def __init__(self, msg):
        super().__init__(f"invalid register index[{msg}]")
