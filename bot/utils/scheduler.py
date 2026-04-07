"""Session scheduling — anti-detection run/break cycles and daily reset timing."""

from __future__ import annotations

import random
import time
from datetime import datetime, timedelta
from typing import Callable

from loguru import logger


class SessionScheduler:
    """Runs the bot in bursts with randomized idle windows in between.

    Pattern:
        - Active session: `session_hours` +/- 20%
        - Break: `break_minutes` +/- 20%
    Never runs 24/7.
    """

    def __init__(self, session_hours: float, break_minutes: float) -> None:
        self.session_hours = session_hours
        self.break_minutes = break_minutes
        self._session_end: datetime | None = None

    def start_session(self) -> None:
        jitter = 1.0 + random.uniform(-0.2, 0.2)
        duration = timedelta(hours=self.session_hours * jitter)
        self._session_end = datetime.now() + duration
        logger.info(f"Session started, ends at {self._session_end:%H:%M:%S}")

    def should_stop(self) -> bool:
        if self._session_end is None:
            return False
        return datetime.now() >= self._session_end

    def take_break(self) -> None:
        jitter = 1.0 + random.uniform(-0.2, 0.2)
        minutes = self.break_minutes * jitter
        logger.info(f"Break for {minutes:.1f} minutes")
        time.sleep(minutes * 60)

    def run_forever(self, session_fn: Callable[[], None]) -> None:
        while True:
            self.start_session()
            try:
                session_fn()
            except KeyboardInterrupt:
                logger.warning("KeyboardInterrupt — stopping scheduler")
                raise
            except Exception as e:
                logger.exception(f"Session raised: {e}")
            self.take_break()


def seconds_until_daily_reset(reset_utc_hour: int = 4) -> float:
    """Seconds remaining until daily AFK Arena reset (04:00 UTC)."""
    now = datetime.utcnow()
    next_reset = now.replace(hour=reset_utc_hour, minute=0, second=0, microsecond=0)
    if next_reset <= now:
        next_reset += timedelta(days=1)
    return (next_reset - now).total_seconds()
