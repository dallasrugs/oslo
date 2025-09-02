# file: console-api/app/internal/logger.py

import logging

# Configure root logger once
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)  # or DEBUG, WARNING, ERROR

# Avoid adding multiple handlers if imported multiple times
if not logger.handlers:
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)