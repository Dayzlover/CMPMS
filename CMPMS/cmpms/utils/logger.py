import logging
import os
from pathlib import Path


def setup_logger() -> logging.Logger:
    # Project root
    root = Path(__file__).resolve().parents[2]

    # Log directory
    log_dir = root / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "cmpms.log"

    logger = logging.getLogger("CMPMS")

    # Prevent duplicate handlers if the bot is restarted
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        "%d/%m/%Y %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger