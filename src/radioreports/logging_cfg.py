# src/radioreports/logging_cfg.py
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

FMT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging(level: str = "INFO", log_dir: str | Path = "output") -> None:
    """Базове налаштування логування у консоль + файл з ротацією."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_file = Path(log_dir) / "app.log"

    # Базова конфігурація (консоль)
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format=FMT)

    # Ротація файлу (до ~500KB, 3 копії)
    fh = RotatingFileHandler(log_file, maxBytes=500_000, backupCount=3, encoding="utf-8")
    fh.setFormatter(logging.Formatter(FMT))
    logging.getLogger().addHandler(fh)
