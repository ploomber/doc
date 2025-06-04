import logging
from typing import final
from fastapi import Request
from src.settings import Settings

async def get_logger(request: Request) -> logging.Logger:
    return request.app.state.logger

@final
class CustomFormatter(logging.Formatter):
    """Custom formatter that includes timestamp, level, and location"""
    
    grey = "\x1b[38;5;243m"
    blue = "\x1b[38;5;109m"      
    yellow = "\x1b[38;5;214m"    
    red = "\x1b[38;5;167m"       
    bold_red = "\x1b[38;5;203m"  
    reset = "\x1b[0m"

    dev_format = (
        "%(asctime)s - %(levelname)s - %(message)s "
        "(%(filename)s:%(lineno)d)"
    )
    
    # Prod format - copy like uvicorn (+file/line info)
    prod_format = (
        "%(levelname)s:     %(message)s "
        "(%(filename)s:%(lineno)d)"
    )

    def __init__(self, is_prod: bool = False):
        super().__init__()
        if is_prod:
            self.formats = {
                logging.DEBUG: self.prod_format,
                logging.INFO: self.prod_format,
                logging.WARNING: self.prod_format,
                logging.ERROR: self.prod_format,
                logging.CRITICAL: self.prod_format
            }
        else:
            self.formats = {
                logging.DEBUG: self.grey + self.dev_format + self.reset,
                logging.INFO: self.blue + self.dev_format + self.reset,
                logging.WARNING: self.yellow + self.dev_format + self.reset,
                logging.ERROR: self.red + self.dev_format + self.reset,
                logging.CRITICAL: self.bold_red + self.dev_format + self.reset
            }


    def format(self, record):
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logging(settings: Settings) -> logging.Logger:
    """
    Setup application logging with custom formatting and level
    
    Args:
        settings: Application settings containing LOG_LEVEL and PROFILE
        
    Returns:
        Logger instance configured for the application
    """
    # Configure the root logger first to prevent duplicate logs
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    logger = logging.getLogger("app")
    logger.handlers.clear()
    logger.propagate = False
    
    # Set level from settings
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create console handler with custom formatter
    console_handler = logging.StreamHandler()
    is_prod = settings.PROFILE == "PROD"
    console_handler.setFormatter(CustomFormatter(is_prod=is_prod))
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Clear handlers for common libraries that might have their own loggers
    for logger_name in ["asyncio", "uvicorn", "uvicorn.access"]:
        lib_logger = logging.getLogger(logger_name)
        lib_logger.handlers.clear()
        lib_logger.propagate = True  # Let these propagate to the root
    
    # Set up a simple root handler that forwards to our app logger
    class RootHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            # Skip our own app logs to prevent loops
            if not record.name.startswith("app"):
                msg = f"{record.name}: {record.getMessage()}"
                if record.exc_info:
                    # If there's an exception, include its details
                    import traceback
                    exc_type, exc_value, exc_traceback = record.exc_info
                    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                    msg += f"\nException details:\n{''.join(tb_lines)}"
                logger.log(record.levelno, msg)
    
    root_handler = RootHandler()
    root_logger.addHandler(root_handler)
    
    return logger

class LogConfig:
    """Logging configuration"""
    
    # Define format for the logs
    LOGGER_NAME: str = "app"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config dict
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": LOG_FORMAT,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
        },
    }

