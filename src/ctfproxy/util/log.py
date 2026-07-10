import logging
import sys
from rich.console import Console

SUCCESS_LEVEL_NUM = 25
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

def success(self, message, *args, **kws):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)

logging.Logger.success = success
console = Console()

class CustomFormatter(logging.Formatter):
    def formatException(self, ei):
        exc_type, exc_value, _ = ei
        return f"{exc_type.__name__}: {exc_value}"

class RichConsoleFormatter(CustomFormatter):
    def format(self, record):
        message = super().format(record)
        
        level = record.levelno
        if level == logging.DEBUG:
            prefix = r"\[[magenta bold]DEBUG[/magenta bold]]"
            return f"{prefix} {message}"
        elif level == logging.INFO:
            prefix = r"\[[magenta bold]INFO[/magenta bold]]"
            return f"{prefix} {message}"
        elif level == SUCCESS_LEVEL_NUM:
            prefix = r"\[[magenta bold]SUCC[/magenta bold]]"
            return f"{prefix} [green]{message}[/green]"
        elif level == logging.WARNING:
            prefix = r"\[[magenta bold]WARN[/magenta bold]]"
            return f"{prefix} [yellow]{message}[/yellow]"
        elif level >= logging.ERROR:
            prefix = r"\[[magenta bold]ERROR[/magenta bold]]"
            return f"{prefix} [red]{message}[/red]"
        return message

class PlainFileFormatter(CustomFormatter):
    def format(self, record):
        message = super().format(record)
        asctime = self.formatTime(record, self.datefmt)
        
        level = record.levelno
        if level == logging.DEBUG:
            prefix = "[DEBUG]"
        elif level == logging.INFO:
            prefix = "[INFO]"
        elif level == SUCCESS_LEVEL_NUM:
            prefix = "[SUCC]"
        elif level == logging.WARNING:
            prefix = "[WARN]"
        elif level >= logging.ERROR:
            prefix = "[ERROR]"
        else:
            prefix = f"[{record.levelname}]"
            
        return f"{asctime} {prefix} {message}"

class RichConsoleHandler(logging.Handler):
    def __init__(self, stream=None):
        super().__init__()
        self.console = Console(file=stream)

    def emit(self, record):
        try:
            msg = self.format(record)
            if record.levelno == logging.DEBUG:
                try:
                    self.console.log(msg, _stack_offset=7)
                except Exception:
                    self.console.log(msg)
            else:
                self.console.print(msg)
        except Exception:
            self.handleError(record)

def initLogging(level=logging.INFO, stream="stdout", file_path=None):
    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        
    root_logger.setLevel(level)

    if stream in ["stdout", "stderr"]:
        stream_obj = sys.stdout if stream == "stdout" else sys.stderr
        console_handler = RichConsoleHandler(stream=stream_obj)
        console_handler.setLevel(level)
        console_handler.setFormatter(RichConsoleFormatter())
        root_logger.addHandler(console_handler)

    if file_path:
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(PlainFileFormatter())
        root_logger.addHandler(file_handler)
