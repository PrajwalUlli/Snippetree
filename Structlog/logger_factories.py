# Standard-lib Modules
import sys
from typing import IO

# PyPI Modules
import structlog


class DualStreamLogger:
    """Custom logger that writes to file and conditionally to console."""

    def __init__(self, file_handle: IO[str]):
        self.filename = file_handle.name
        self.file_logger = structlog.WriteLogger(file_handle)
        self.console_logger = structlog.WriteLogger(sys.stderr)

    def _log(self, level: str, message: str):
        # translates to "self.file_logger.<level>(message)"
        getattr(self.file_logger, level)(message)

        # Only log errors and above to console with simple message
        if level in ["error", "critical", "exception"]:
            msg = f"ERROR: Check {self.filename} for detailed error information"
            self.console_logger.info(msg)

    def debug(self, message: str):  # logs only to console
        self.console_logger.info(message)

    def info(self, message: str):  # logs only to console
        self.console_logger.info(message)

    def warning(self, message: str):
        self._log("warning", message)

    def error(self, message: str):
        self._log("error", message)

    def critical(self, message: str):
        self._log("critical", message)

    def exception(self, message: str):
        self._log("exception", message)


class DualStreamLoggerFactory:
    def __init__(self, file_handle: IO[str] | None = None):
        self.file_handle = file_handle

    def __call__(self, *args):
        return DualStreamLogger(self.file_handle)


class NullLogger:
    """A logger that does nothing when logging is disabled."""

    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def critical(self, *args, **kwargs):
        pass

    def exception(self, *args, **kwargs):
        pass

    def bind(self, **kwargs):
        return self

    def unbind(self, *args):
        return self

    def new(self, **kwargs):
        return self


class KeyOrderProcessor:
    """Processor class to reorder keys in event dictionaries."""

    def __init__(self, key_order: dict[str, str] | None = None):
        self.key_order = key_order or ["level", "time", "event", "filename", "func_name", "lineno"]

    def __call__(self, logger: DualStreamLogger, method_name: str, event_dict: dict[str, str]):
        """Reorder keys in the event dictionary."""
        ordered_dict = {}

        # Add keys in specified order
        for key in self.key_order:
            if key in event_dict:
                ordered_dict[key] = event_dict[key]

        # Add any remaining keys
        for key, value in event_dict.items():
            if key not in ordered_dict:
                ordered_dict[key] = value

        return ordered_dict
