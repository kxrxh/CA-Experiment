class MachineException(Exception):
    """Base class for machine-related exceptions."""
    pass


class StopIteration(MachineException):
    """Exception raised to signal the end of iteration."""

    def __init__(self, msg):
        super().__init__(f"StopIteration: {msg}")


class MachineRuntimeError(MachineException):
    """Exception raised for runtime errors."""

    def __init__(self, msg):
        super().__init__(f"Runtime Error: {msg}")


class InvalidRegisterIndex(MachineRuntimeError):
    """Exception raised for invalid register index."""

    def __init__(self, msg):
        super().__init__(f"Invalid Register Index: {msg}")
