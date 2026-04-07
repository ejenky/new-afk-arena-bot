"""Hero leveling — quick daily level-up and RC Cramming logic."""

from __future__ import annotations

import time

from .base import BaseTask
from ..strategy.progression import Phase, detect_phase, should_rc_cram


class LevelHeroesTask(BaseTask):
    name = "level_heroes"

    def quick_level(self) -> bool:
        """Level a single hero for the daily quest checkbox."""
        self.log("leveling one hero (daily)")
        if not self.nav.goto_heroes(self.adb, self.vision):
            return False
        # Tap top-left hero portrait.
        self.adb.tap(200, 500)
        time.sleep(1.0)
        self.vision.wait_and_tap(self.adb, "buttons/level_up.png", timeout=5)
        self.popup.dismiss_all(self.adb, self.vision)
        return True

    def rc_cramming(self, max_levels: int = 20) -> bool:
        """Phase 3 only: pump EXP/Dust into the current Resonating Cross carry."""
        chapter = self.state.get("current_chapter", 1) if self.state else 1
        if not should_rc_cram(detect_phase(chapter)):
            return False
        self.log("RC Cramming — pumping top hero to max level")
        if not self.nav.goto_heroes(self.adb, self.vision):
            return False
        self.adb.tap(200, 500)
        time.sleep(1.0)
        leveled = 0
        for _ in range(max_levels):
            if not self.vision.wait_and_tap(self.adb, "buttons/level_up.png", timeout=2):
                break
            leveled += 1
            time.sleep(0.4)
        self.popup.dismiss_all(self.adb, self.vision)
        self._record("rc_cram", f"+{leveled} levels")
        return True

    def run(self) -> bool:
        self.quick_level()
        self.rc_cramming()
        return True
