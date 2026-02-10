from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional


def setup_logger(log_dir: Optional[Path] = None) -> logging.Logger:
    """Set up a logger that writes to a file and the console.

    Parameters
    ----------
    log_dir: Path, optional
        Directory where log files should be stored. If not provided,
        the `logs` directory in the project root will be used.

    Returns
    -------
    logging.Logger
        A configured logger instance.
    """
    project_root = Path(__file__).resolve().parent.parent
    if log_dir is None:
        log_dir = project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    logger = logging.getLogger("downloads_organizer")
    logger.setLevel(logging.INFO)

    # Only add handlers once
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger
