from enum import Enum, auto

class LT (Enum):
    INFO = auto()
    SUCCESS = auto()
    WARN = auto()
    ERROR = auto()
    EXIT = auto()


def log(type, *args, **kwargs):
    pass
