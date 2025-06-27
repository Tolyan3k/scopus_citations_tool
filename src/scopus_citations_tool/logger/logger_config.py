import sys

from loguru import logger


LOG_FILENAME_DEFAULT = ".log"


def config_logger(log_filename: str) -> None:
    log_config = {
        "handlers": [
            {
                "sink": sys.stdout,
                "level": "INFO",
                "format": "{message}",
                "filter": lambda lvl: lvl["level"].no < 30,
            },
            {
                "sink": sys.stdout,
                "format": "{level}: {message}",
                "filter": lambda lvl: lvl["level"].name == "ERROR",
            },
            {
                "sink": log_filename,
                "mode": "w",
                "level": "TRACE",
                "format": "{level}:{name}:{file}:{function}:{line}: {message}",
            },
        ],
    }
    logger.configure(**log_config)
