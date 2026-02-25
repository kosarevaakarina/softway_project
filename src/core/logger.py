import logging
import os
import sys

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logger = logging.getLogger("softway")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

log_dir = os.getenv("LOG_DIR", None)
if log_dir:
    os.makedirs(log_dir, exist_ok=True)

    error_handler = logging.FileHandler(
        os.path.join(log_dir, "error.log"), encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    debug_handler = logging.FileHandler(
        os.path.join(log_dir, "debug.log"), encoding="utf-8"
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.addFilter(lambda record: record.levelno < logging.ERROR)
    debug_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)
