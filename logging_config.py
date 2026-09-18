"""
Central logging configuration.

Call `setup_logging()` once from an entry point (gui.py, streamlit_app.py,
scheduler.py's headless path) to get consistent, timestamped logs on both
the console and a rotating file under logs/. Safe to call more than once —
it no-ops if the root logger is already configured.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "tracker.log")


def setup_logging():
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return  # already configured — e.g. Streamlit reruns this on every interaction

    os.makedirs(LOG_DIR, exist_ok=True)
    root_logger.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
