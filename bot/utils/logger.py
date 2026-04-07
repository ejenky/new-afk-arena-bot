"""Loguru configuration with rotating file sink and rich console output."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger


def setup_logger(logs_dir: Path, level: str = "INFO") -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <7}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
    )
    logs_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        logs_dir / "bot_{time:YYYYMMDD}.log",
        level="DEBUG",
        rotation="10 MB",
        retention="14 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <7} | "
               "{name}:{function}:{line} - {message}",
        enqueue=True,
    )
