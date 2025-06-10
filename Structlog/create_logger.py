# Standard-lib Modules
import os
import sys

# PyPI Modules
import structlog

# Local Modules
from .logger_factories import DualStreamLoggerFactory, KeyOrderProcessor, NullLogger


def no_logging():
    structlog.configure(
        processors=[],
        logger_factory=lambda: NullLogger(),
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger()


def yes_logging(log_file_path: str | None):
    # Get the filename for where this module is currently imported
    basename = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    # Open file once and keep it open
    file = log_file_path or f"{basename}.log"
    log_file = open(file, "a")  # noqa SIM115

    # Configuration
    structlog.configure(
        # The processors keep adding to the even container and pass it onto the next one,
        # finally the JSONRenderer converts it to a json format
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            ),
            structlog.processors.TimeStamper(fmt="%M:%S", key="time"),
            structlog.processors.format_exc_info,
            KeyOrderProcessor(),  # Custom processor to reorder keys
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=DualStreamLoggerFactory(log_file),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


def setup_logging(enable_log: bool, log_file_path: str | None = None):
    """Configure structlog with optional logging."""
    if not enable_log:
        return no_logging()
    return yes_logging(log_file_path)
