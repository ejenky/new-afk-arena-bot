"""Smart summoning — coordinate-driven, popup-handler protected."""

from __future__ import annotations

import time

from .base import BaseTask
from .. import coords
from ..strategy.progression import detect_phase, should_summon


class SummonTask(BaseTask):
    name = "summon"

    def _dismiss(self) -> None:
        self.popup.dismiss_all(self.adb, self.vision)

    def single_free(self) -> bool:
        self.log("claiming single free summon")
        self.nav.goto_tavern(self.adb, self.vision)
        time.sleep(1.0)
        self.adb.tap(*coords.TAVERN_NOBLE_ENTRY)
        time.sleep(1.2)
        self.adb.tap(*coords.TAVERN_FREE_SUMMON)
        time.sleep(1.0)
        self._dismiss()
        self.adb.tap(*coords.TAVERN_FREE_COLLECT)
        time.sleep(0.8)
        self._dismiss()
        self._record("summon", "free_single")
        return True

    def ten_pull_faction(self) -> bool:
        """Use faction summon scrolls for a 10x pull.

        Safe: faction scrolls are not a diamond cost. The popup blacklist
        will still block any unexpected diamond confirmation.
        """
        self.log("attempting 10x faction pull")
        self.nav.goto_tavern(self.adb, self.vision)
        time.sleep(1.0)
        self.adb.tap(*coords.TAVERN_NOBLE_ENTRY)
        time.sleep(1.0)
        self.adb.tap(*coords.TAVERN_FACTION_TAB)
        time.sleep(0.8)
        self.adb.tap(*coords.TAVERN_SUMMON_10X)
        time.sleep(0.8)
        self.adb.tap(*coords.BTN_CONFIRM)
        time.sleep(1.5)
        self._dismiss()
        self._record("summon", "faction_10x")
        return True

    def ten_pull_diamonds(self) -> bool:
        """Spend diamonds on a 10x pull — phases 1 & 2 only."""
        chapter = self.state.get("current_chapter", 1) if self.state else 1
        if not should_summon(detect_phase(chapter)):
            self.log(f"phase 3 (ch{chapter}) — skipping diamond summons")
            return False
        self.log("attempting 10x diamond pull")
        self.nav.goto_tavern(self.adb, self.vision)
        time.sleep(1.0)
        self.adb.tap(*coords.TAVERN_NOBLE_ENTRY)
        time.sleep(1.0)
        self.adb.tap(*coords.TAVERN_ALL_HERO_TAB)
        time.sleep(0.8)
        self.adb.tap(*coords.TAVERN_SUMMON_10X)
        time.sleep(0.8)
        self.adb.tap(*coords.BTN_CONFIRM)
        time.sleep(2.0)
        self._dismiss()
        self._record("summon", "diamond_10x")
        return True

    def run(self) -> bool:
        self.single_free()
        self.ten_pull_faction()
        self.ten_pull_diamonds()
        return True
