"""
A sample logger (requires structlog, tested with structlog==25.1.0)

Usage
-----

>>> from $package_name.log import configure_file_and_print_logger, get_logger
>>> configure_file_and_print_logger("app.log")
>>> # OR
>>> configure_print_logger()
>>> logger = get_logger()
>>> logger.info("Hello, world!")
"""

import logging
from typing import Any, TextIO
import os

import structlog
from structlog import WriteLogger, PrintLogger


class CustomLogger:
    """
    A custom logger that writes to a file and prints to the console
    """

    def __init__(self, file: TextIO | None = None):
        self._file = file
        self._write_logger = WriteLogger(self._file)
        self._print_logger = PrintLogger()

    def msg(self, message: str) -> None:
        self._write_logger.msg(message)
        self._print_logger.msg(message)

    log = debug = info = warn = warning = msg
    fatal = failure = err = error = critical = exception = msg


class CustomLoggerFactory:
    def __init__(self, file: TextIO | None = None):
        self._file = file

    def __call__(self, *args: Any) -> CustomLogger:
        return CustomLogger(self._file)


def configure_file_and_print_logger(file_path: str = "app.log") -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
        context_class=dict,
        logger_factory=CustomLoggerFactory(open(file_path, "at")),
        cache_logger_on_first_use=False,
    )


def configure_print_logger() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def configure_no_logging() -> None:
    structlog.configure(
        logger_factory=structlog.PrintLoggerFactory(open(os.devnull, "w")),
    )


def get_logger():
    return structlog.get_logger()
