import logging
import subprocess
import sys
from logging.handlers import TimedRotatingFileHandler

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def level_from_settings(setting_name: str) -> int:
    try:
        level_str = getattr(settings, setting_name)
    except AttributeError:
        raise ValueError(f"Name '{setting_name}' was not found in Django settings!")
    try:
        return logging.getLevelNamesMapping()[level_str]
    except KeyError:
        raise ImproperlyConfigured(f"Coundn't parse logging level '{level_str}'!")


def get_logger() -> logging.Logger:
    console_level = level_from_settings("CONSOLE_LOG_LEVEL")
    file_level = level_from_settings("FILE_LOG_LEVEL")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    subprocess.run(["mkdir", "-p", settings.LOG_DIR], capture_output=True, check=True)
    file_handler = TimedRotatingFileHandler(
        f"{settings.LOG_DIR}/log.txt",
        when="midnight",  # rotate once per month at midnight
        interval=30,  # ~monthly rotation (in days)
        backupCount=12,  # Keep a year's worth of backups
        utc=True,
    )
    file_handler.setLevel(file_level)
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
