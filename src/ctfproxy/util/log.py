from enum import Enum, auto

from rich.console import Console

class LT (Enum):
    INFO = auto()
    SUCCESS = auto()
    WARN = auto()
    ERROR = auto()
    EXIT = auto()
    DEBUG = auto()

console = Console()

def log(type, *args, **kwargs):
    printfunc = console.print
    if type == LT.EXIT or type == LT.ERROR:
        console.print(r"\[[magenta bold]ERROR[/magenta bold]] [red]", *args, style="red", **kwargs)
    elif type == LT.WARN:
        console.print(r"\[[magenta bold]WARN[/magenta bold]] [yellow]", *args, style="yellow", **kwargs)
    elif type == LT.SUCCESS:
        console.print(r"\[[magenta bold]SUCC[/magenta bold]] [green]", *args, style="green", **kwargs)
    elif type == LT.DEBUG:
        console.log(r"\[[magenta bold]DEBUG[/magenta bold]] ", *args, **kwargs)
    else: # INFO
        console.print(r"\[[magenta bold]INFO[/magenta bold]] ", *args, **kwargs)
