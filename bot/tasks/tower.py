"""King's Tower and Faction Towers push — coordinate-driven.

Template matching is retained ONLY for Victory / Defeat banner detection
after each battle.
"""

from __future__ import annotations

import time
from typing import Optional

from .base import BaseTask
from .. import coords


class TowerTask(BaseTask):
    name = "tower"

    def _battle_result(self, timeout: int = 180) -> Optional[str]:
        start = time.time()
        while time.time() - start < timeout:
            shot = self.adb.screenshot()
            if self.vision.find(shot, "screens/victory.png", 0.70):
                return "victory"
            if self.vision.find(shot, "screens/defeat.png", 0.70):
                return "defeat"
            time.sleep(2)
        return None

    def _dismiss(self) -> None:
        self.popup.dismiss_all(self.adb, self.vision)

    def kings_tower(self, max_attempts: int = 50) -> bool:
        self.log("starting King's Tower push")
        self.nav.goto_kings_tower(self.adb, self.vision)
        time.sleep(1.0)
        self.adb.tap(*coords.KT_ENTER)  # Enter main King's Tower
        time.sleep(1.5)

        failures = 0
        for _ in range(max_attempts):
            self._dismiss()
            self.adb.tap(*coords.KT_CHALLENGE)
            time.sleep(1.0)
            self._dismiss()
            self.adb.tap(*coords.KT_BATTLE_BEGIN)
            result = self._battle_result()
            if result == "victory":
                failures = 0
                self._dismiss()
                self.adb.tap(*coords.KT_CONTINUE_AFTER_WIN)
                self._record("kt_win", "")
            elif result == "defeat":
                failures += 1
                self.adb.tap(*coords.BTN_CONFIRM_CENTER)
                if failures >= 3:
                    self.log("stuck on King's Tower — stopping for today")
                    return False
            else:
                self.log("unknown battle result — dismissing popups")
                self._dismiss()
        return True

    def faction_tower(self, faction_coord, max_attempts: int = 15) -> bool:
        self.log(f"starting faction tower {faction_coord}")
        self.nav.goto_kings_tower(self.adb, self.vision)
        time.sleep(1.0)
        self.adb.tap(*faction_coord)
        time.sleep(1.5)
        return self.kings_tower(max_attempts=max_attempts)

    def run(self) -> bool:
        ok = self.kings_tower()
        for ft in (
            coords.KT_TOWER_LIGHTBEARER,
            coords.KT_TOWER_MAULER,
            coords.KT_TOWER_WILDER,
            coords.KT_TOWER_GRAVEBORN,
        ):
            try:
                self.faction_tower(ft, max_attempts=15)
            except Exception as e:
                self.log(f"faction tower {ft} failed: {e}")
                self._dismiss()
        return ok
