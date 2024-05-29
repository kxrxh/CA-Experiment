class MachineRuntimeError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class InvalidRegisterIndex(MachineRuntimeError):
    def __init__(self, msg):
        super().__init__(f"Invalid register index: {msg}")
