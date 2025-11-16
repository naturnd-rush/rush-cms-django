import logging
import subprocess
import sys
from logging.handlers import TimedRotatingFileHandler

from django.conf import settings


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Lowest common denominator allows the handlers to decide.
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.CONSOLE_LOG_LEVEL)
    subprocess.run(["mkdir", "-p", settings.LOG_DIR], capture_output=True, check=True)
    file_handler = TimedRotatingFileHandler(
        f"{settings.LOG_DIR}/log.txt",
        when="midnight",  # rotate once per month at midnight
        interval=30,  # ~monthly rotation (in days)
        backupCount=12,  # Keep a year's worth of backups
        utc=True,
    )
    file_handler.setLevel(settings.FILE_LOG_LEVEL)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s]: %(message)s",
        datefmt="%Y-%m-%d_%I-%M-%S_%p_%Z%z",
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger
