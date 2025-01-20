from __future__ import annotations

import sys

from loguru import logger

def filter_info_debug_warning(record):
    """Filter out INFO, DEBUG, and WARNING messages.
    
    Params:
        record (dict): The log record to filter.
    
    Returns:
        bool: True if the log record should be filtered out, False otherwise.

    """
    return record["level"].name in ["WARNING", "INFO", "DEBUG"]

def filter_debug_only(record):
    """Filter out INFO, DEBUG, and WARNING messages.
    
    Params:
        record (dict): The log record to filter.
    
    Returns:
        bool: True if the log record should be filtered out, False otherwise.

    """
    return record["level"].name == "DEBUG"

def filter_error_only(record):
    """Filter out INFO, DEBUG, and WARNING messages.
    
    Params:
        record (dict): The log record to filter.
    
    Returns:
        bool: True if the log record should be filtered out, False otherwise.

    """
    return record["level"].name == "ERROR"

def filter_trace_only(record):
    """Filter out INFO, DEBUG, and WARNING messages.
    
    Params:
        record (dict): The log record to filter.
    
    Returns:
        bool: True if the log record should be filtered out, False otherwise.

    """
    return record["level"].name == "TRACE"

def filter_all_errors(record):
    """Filter out INFO, DEBUG, and WARNING messages.
    
    Params:
        record (dict): The log record to filter.
    
    Returns:
        bool: True if the log record should be filtered out, False otherwise.

    """
    return record["level"].name in ["ERROR", "TRACE"]

def setup_loguru_logging(
    log_level: str = "INFO",
    enable_loggers: list[str] = ["spacetraders_data"],
    add_file_logger: bool = False,
    app_log_file: str = "logs/app.log",
    add_error_file_logger: bool = False,
    error_log_file: str = "logs/error.log",
    colorize: bool = False,
    retention: int = 3,
    rotation: str = "15 MB",
    log_fmt: str = "detailed"
):
    """Setup loguru logging.

    Params:
        log_level (str): The log level to use.
        enable_loggers (list[str]): A list of loggers to enable.
        add_file_logger (bool): If `True`, add a file logger to the log.
        add_error_file_logger (bool): If `True`, add a file logger to the log for errors.
        colorize (bool): If `True`, colorize the log output.
    """
    valid_log_fmts: list[str] = ["basic", "detailed"]

    fmt_basic: str = "{time:YY-MM-DD HH:mm:ss} [{level}]: {message}"
    fmt_basic_color: str = "<blue>{time:YY-MM-DD HH:mm:ss}</> [<yellow>{level}</>]: {message}"
    
    fmt_detailed: str = "{time:YYYY-MM-DD HH:mm:ss} | [{level}] | ({module}.{function}:{line}) | > {message}"
    fmt_detailed_color: str = "<blue>{time:YYYY-MM-DD HH:mm:ss}</> | [<yellow>{level}</>] | (<cyan>{module}.{function}:{line}</>) | > {message}"
    
    match log_fmt.lower():
        case "basic":
            if colorize:
                fmt = fmt_basic_color
            else:
                fmt = fmt_basic        
        case "detailed":
            if colorize:
                fmt = fmt_detailed_color
            else:
                fmt = fmt_detailed
        case _:
            raise ValueError(f"Unknown log_fmt: '{log_fmt}'. Must be one of {valid_log_fmts}")
            
    logger.remove(0)
    logger.add(
        sys.stderr,
        format=fmt,
        level=log_level,
        colorize=colorize
    )

    if enable_loggers:
        for _logger in enable_loggers:
            logger.enable(_logger)

    if add_file_logger:
        logger.add(app_log_file, format=fmt, retention=retention, rotation=rotation, level="DEBUG")

    if add_error_file_logger:
        logger.add(error_log_file, format=fmt, retention=retention, rotation=rotation, level="ERROR")
