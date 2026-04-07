"""Smart summoning — single free daily, 10x faction scroll, 10x diamond pulls."""

from __future__ import annotations

import time

from .base import BaseTask
from ..strategy.progression import Phase, detect_phase, should_summon


class SummonTask(BaseTask):
    name = "summon"

    def single_free(self) -> bool:
        self.log("claiming single free summon")
        if not self.nav.goto_tavern(self.adb, self.vision):
            return False
        self.popup.dismiss_all(self.adb, self.vision)
        if self.vision.wait_and_tap(self.adb, "buttons/free_summon.png", timeout=5):
            self.popup.dismiss_all(self.adb, self.vision)
            self._record("summon", "free_single")
            return True
        return False

    def ten_pull_faction(self) -> bool:
        """Use faction summon scrolls for a 10x pull if 10 are available."""
        self.log("attempting 10x faction pull")
        if not self.nav.goto_tavern(self.adb, self.vision):
            return False
        self.vision.wait_and_tap(self.adb, "icons/faction_summon.png", timeout=5)
        time.sleep(1.0)
        if self.vision.wait_and_tap(self.adb, "buttons/summon_10x.png", timeout=5):
            self.vision.wait_and_tap(self.adb, "buttons/confirm.png", timeout=3)
            self.popup.dismiss_all(self.adb, self.vision)
            self._record("summon", "faction_10x")
            return True
        return False

    def ten_pull_diamonds(self) -> bool:
        """Spend diamonds on a 10x pull — ONLY during phases 1 & 2."""
        chapter = self.state.get("current_chapter", 1) if self.state else 1
        if not should_summon(detect_phase(chapter)):
            self.log(f"phase 3 (ch{chapter}) — skipping diamond summons")
            return False
        self.log("attempting 10x diamond pull")
        if not self.nav.goto_tavern(self.adb, self.vision):
            return False
        self.vision.wait_and_tap(self.adb, "icons/all_hero_summon.png", timeout=5)
        time.sleep(1.0)
        if self.vision.wait_and_tap(self.adb, "buttons/summon_10x_diamond.png", timeout=5):
            self.vision.wait_and_tap(self.adb, "buttons/confirm.png", timeout=3)
            self.popup.dismiss_all(self.adb, self.vision)
            self._record("summon", "diamond_10x")
            return True
        return False

    def run(self) -> bool:
        self.single_free()
        self.ten_pull_faction()
        self.ten_pull_diamonds()
        return True
