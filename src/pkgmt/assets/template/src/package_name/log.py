import logging
from typing import Any
from pathlib import Path
from copy import deepcopy

import structlog
from structlog import WriteLogger, PrintLogger


class MultiRendererLoggerFactory:
    def __init__(
        self,
        *,
        console_processors: list,
        json_processors: list,
        console_renderer: Any,
        json_renderer: Any,
        console_logger: Any,
        json_logger: Any,
    ):
        self._console_processors = console_processors
        self._json_processors = json_processors
        self._console_renderer = console_renderer
        self._json_renderer = json_renderer
        self._console_logger = console_logger
        self._json_logger = json_logger

    def __call__(self, *args: Any) -> "MultiRendererLogger":
        return MultiRendererLogger(
            console_processors=self._console_processors,
            json_processors=self._json_processors,
            console_renderer=self._console_renderer,
            json_renderer=self._json_renderer,
            console_logger=self._console_logger,
            json_logger=self._json_logger,
        )


class MultiRendererLogger:
    """
    A custom logger that writes JSON to a file and pretty prints to the console
    """

    def __init__(
        self,
        *,
        console_processors: list,
        json_processors: list,
        console_renderer: Any,
        json_renderer: Any,
        console_logger: Any,
        json_logger: Any,
    ):
        self._console_processors = console_processors
        self._json_processors = json_processors
        self._console_renderer = console_renderer
        self._json_renderer = json_renderer
        self._console_logger = console_logger
        self._json_logger = json_logger

    def msg(self, **kwargs) -> None:
        kwargs_json = deepcopy(kwargs)
        kwargs_console = deepcopy(kwargs)

        for processor in self._console_processors:
            processor(self, "logger", kwargs_console)

        for processor in self._json_processors:
            processor(self, "logger", kwargs_json)

        message_console = self._console_renderer(self, "logger", kwargs_console)
        message_json = self._json_renderer(self, "logger", kwargs_json)

        self._console_logger.msg(message_console)
        self._json_logger.msg(message_json)

    log = debug = info = warn = warning = msg
    fatal = failure = err = error = critical = exception = msg


def configure_multi_renderer_logger(
    file_path: str = "app.log",
    level: int = logging.INFO,
    colors: bool = True,
) -> None:
    """
    Configure a logger that writes JSON formatted logs to a file while using
    the console renderer for terminal output.

    Parameters
    ----------
    file_path : str, optional
        Path to the log file, by default "app.log"
    """
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        # to add filename, function name, and line number to the log record
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ],
        ),
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
        # NOTE: we don't pass a renderer here, since we'll use a different
        # renderer for the console and the file
    ]

    json_processors = [
        # dict tracebacks renders tracebacks as a dict
        # structlog.processors.dict_tracebacks,
        # format exc info renders tracebacks as a string
        structlog.processors.format_exc_info,
    ]

    console_processors = []

    if colors:
        console_processors.append(structlog.dev.set_exc_info)
    else:
        console_processors.append(structlog.processors.format_exc_info)

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=MultiRendererLoggerFactory(
            console_processors=console_processors,
            json_processors=json_processors,
            console_renderer=structlog.dev.ConsoleRenderer(
                colors=colors,
                exception_formatter=structlog.dev.RichTracebackFormatter(
                    show_locals=False,
                    max_frames=3,
                    width=80,
                ),
            ),
            json_renderer=structlog.processors.JSONRenderer(),
            json_logger=WriteLogger(Path(file_path).open("at")),
            console_logger=PrintLogger(),
        ),
        cache_logger_on_first_use=False,
        processors=processors,
    )


def get_logger():
    return structlog.get_logger()
