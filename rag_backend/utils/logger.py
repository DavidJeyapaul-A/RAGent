import logging
import os
from datetime import datetime
import random
import string

# ---------------- this is for local testing purposes ----------------
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
# --------------------------------------------------------------------

_loggers = {}

def generate_log_file_path(base_dir="logs"):
    now = datetime.now()
    time_path = now.strftime("%Y/%m/%d/%H")
    full_path = os.path.join(base_dir, time_path)
    os.makedirs(full_path, exist_ok=True)

    serial = now.strftime("%M%S")
    rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    filename = f"{serial}_{rand_str}.log"
    return os.path.join(full_path, filename)

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger instance with file logging and optional local streaming.
    Name should typically be __name__ to capture module.
    """
    # Import settings here to avoid circular import
    from rag_backend.config import settings

    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if getattr(settings, 'local_logging_enabled', False):
        log_file_path = generate_log_file_path()
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s ==> %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Add local streamer (console output) if enabled
    if getattr(settings, 'local_stream_enabled', False):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s ==> %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S"
        )
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)

    if not logger.hasHandlers():
        logger.addHandler(logging.NullHandler())

    _loggers[name] = logger
    return logger


# ─────────────────────────────────────────────
# 👇 Example usage (for testing/demo only)

# if __name__ == "__main__":
#     # class DummySettings:
#         # local_logging_enabled = False
#         # local_stream_enabled = True  # Enable local streamer for testing

#     # settings = DummySettings()

#     log = get_logger("pdf_loader")
#     log.debug("PDF loading started")
#     log.info("Extracted 3 pages from input.pdf")
#     log.warning("Missing metadata on page 2")
