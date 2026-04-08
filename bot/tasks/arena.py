"""Arena of Heroes + Legends' Challenger — coordinate-driven."""

from __future__ import annotations

import time

from .base import BaseTask
from .. import coords


class ArenaTask(BaseTask):
    name = "arena"

    def _dismiss(self) -> None:
        self.popup.dismiss_all(self.adb, self.vision)

    def quick_battles(self, count: int = 5) -> bool:
        """Spend all daily Arena of Heroes tickets (default 5).

        Picks the weakest opponent (slot 5) each time.
        """
        self.log(f"running {count} Arena of Heroes battles")
        self.nav.goto_arena(self.adb, self.vision)
        time.sleep(1.0)

        for i in range(count):
            self._dismiss()
            self.adb.tap(*coords.ARENA_AOH_BATTLE)
            time.sleep(1.2)
            # Pick weakest opponent (bottom slot).
            self.adb.tap(*coords.ARENA_PICK_WEAKEST)
            time.sleep(1.0)
            self.adb.tap(*coords.ARENA_BATTLE_BEGIN)
            # Let the fight auto-complete.
            time.sleep(60)
            self._dismiss()
            self._record("arena_battle", f"{i+1}/{count}")
        self.adb.tap(*coords.ARENA_COLLECT_REWARDS)
        self._dismiss()
        return True

    def challenger(self) -> bool:
        self.log("running Legends' Challenger Tournament")
        self.nav.goto_challenger(self.adb, self.vision)
        time.sleep(1.0)
        self.adb.tap(*coords.CHALLENGER_ENTER)
        time.sleep(1.0)
        self.adb.tap(*coords.CHALLENGER_BATTLE)
        time.sleep(60)
        self._dismiss()
        return True

    def run(self) -> bool:
        ok = self.quick_battles()
        self.challenger()
        return ok
