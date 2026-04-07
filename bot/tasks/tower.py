"""King's Tower and Faction Towers push."""

from __future__ import annotations

import time
from typing import Optional

from .base import BaseTask


class TowerTask(BaseTask):
    name = "tower"

    def _battle(self, timeout: int = 180) -> Optional[str]:
        start = time.time()
        while time.time() - start < timeout:
            shot = self.adb.screenshot()
            if self.vision.find(shot, "screens/victory.png", 0.82):
                return "victory"
            if self.vision.find(shot, "screens/defeat.png", 0.82):
                return "defeat"
            time.sleep(2)
        return None

    def kings_tower(self, max_attempts: int = 50) -> bool:
        self.log("starting King's Tower push")
        if not self.nav.goto_kings_tower(self.adb, self.vision):
            self.log("could not reach King's Tower")
            return False

        failures = 0
        for _ in range(max_attempts):
            self.popup.dismiss_all(self.adb, self.vision)
            if not self.vision.wait_and_tap(self.adb, "buttons/challenge.png", timeout=5):
                self.log("no challenge button — tower locked or done")
                return True
            time.sleep(1.0)
            self.vision.wait_and_tap(self.adb, "buttons/battle_begin.png", timeout=10)
            result = self._battle()
            if result == "victory":
                failures = 0
                self.popup.dismiss_all(self.adb, self.vision)
                self.adb.tap(540, 1600)
                self._record("kt_win", "")
            elif result == "defeat":
                failures += 1
                self.vision.wait_and_tap(self.adb, "buttons/confirm.png", 5)
                if failures >= 3:
                    self.log("stuck on King's Tower — stopping for today")
                    return False
            else:
                self.popup.dismiss_all(self.adb, self.vision)
        return True

    def faction_tower(self, faction: str, max_attempts: int = 30) -> bool:
        self.log(f"starting {faction} faction tower push")
        if not self.nav.goto_kings_tower(self.adb, self.vision):
            return False
        tmpl = f"icons/tower_{faction.lower()}.png"
        if not self.vision.wait_and_tap(self.adb, tmpl, timeout=5):
            self.log(f"faction tower icon not found: {tmpl}")
            return False
        return self.kings_tower(max_attempts=max_attempts)

    def run(self) -> bool:
        ok = self.kings_tower()
        for faction in ("lightbearer", "mauler", "wilder", "graveborn"):
            try:
                self.faction_tower(faction, max_attempts=15)
            except Exception as e:
                self.log(f"{faction} tower failed: {e}")
                self.popup.dismiss_all(self.adb, self.vision)
        return ok
