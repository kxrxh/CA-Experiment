class MachineError(Exception):
    """Base class for machine-related exceptions."""

    pass


class StopIterationError(MachineError):
    """Exception raised to signal the end of iteration."""

    def __init__(self, msg):
        super().__init__(f"StopIteration: {msg}")


class MachineRuntimeError(MachineError):
    """Exception raised for runtime errors."""

    def __init__(self, msg):
        super().__init__(f"Runtime Error: {msg}")


class WriteOnlyCellError(MachineRuntimeError):
    """Exception raised when attempting to read from a write-only cell."""

    def __init__(self, message="Unable to read from write-only cell"):
        self.message = message
        super().__init__(self.message)


class ReadOnlyCellError(MachineRuntimeError):
    """Exception raised when attempting to write to a read-only cell."""

    def __init__(self, message="Unable to write to read-only cell"):
        self.message = message
        super().__init__(self.message)


class InvalidMuxSignalError(MachineRuntimeError):
    def __init__(self, mux_name: str):
        super().__init__("Invalid Mux Signal: {mux_name}")


class InvalidOperandIndexError(MachineRuntimeError):
    def __init__(self):
        super().__init__("Invalid Operand Index")


class InvalidRegisterIndexError(MachineRuntimeError):
    """Exception raised for invalid register index."""

    def __init__(self, msg):
        super().__init__(f"Invalid Register Index: {msg}")
