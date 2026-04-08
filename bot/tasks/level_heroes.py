"""Hero leveling — coordinate-driven daily level-up and RC Cramming logic."""

from __future__ import annotations

import time

from .base import BaseTask
from .. import coords
from ..strategy.progression import detect_phase, should_rc_cram


class LevelHeroesTask(BaseTask):
    name = "level_heroes"

    def _dismiss(self) -> None:
        self.popup.dismiss_all(self.adb, self.vision)

    def quick_level(self) -> bool:
        """Level a single hero for the daily quest checkbox."""
        self.log("leveling one hero (daily)")
        self.nav.goto_heroes(self.adb, self.vision)
        time.sleep(1.0)
        self.adb.tap(*coords.HEROES_FIRST_PORTRAIT)
        time.sleep(1.0)
        self.adb.tap(*coords.HERO_LEVEL_UP_BUTTON)
        time.sleep(0.6)
        self._dismiss()
        self.adb.back()
        return True

    def rc_cramming(self, max_levels: int = 20) -> bool:
        """Phase 3 only: pump EXP/Dust into the current RC carry."""
        chapter = self.state.get("current_chapter", 1) if self.state else 1
        if not should_rc_cram(detect_phase(chapter)):
            return False
        self.log("RC Cramming — pumping top hero")
        self.nav.goto_heroes(self.adb, self.vision)
        time.sleep(1.0)
        self.adb.tap(*coords.HEROES_FIRST_PORTRAIT)
        time.sleep(1.0)
        for _ in range(max_levels):
            self.adb.tap(*coords.HERO_LEVEL_UP_BUTTON)
            time.sleep(0.4)
        self._dismiss()
        self._record("rc_cram", f"+{max_levels} taps")
        self.adb.back()
        return True

    def run(self) -> bool:
        self.quick_level()
        self.rc_cramming()
        return True
