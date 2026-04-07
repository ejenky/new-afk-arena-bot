"""Base task class — shared construction and logging helpers."""

from __future__ import annotations

from loguru import logger


class BaseTask:
    name: str = "base"

    def __init__(self, adb, vision, popup, navigator, state=None) -> None:
        self.adb = adb
        self.vision = vision
        self.popup = popup
        self.nav = navigator
        self.state = state

    def log(self, msg: str) -> None:
        logger.info(f"[{self.name}] {msg}")

    def _record(self, status: str, details: str = "") -> None:
        if self.state is not None:
            try:
                self.state.log_task(self.name, status, details)
            except Exception as e:
                logger.warning(f"state.log_task failed: {e}")

    def run(self) -> bool:
        raise NotImplementedError
