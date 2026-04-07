"""Arena of Heroes + Legends' Challenger Tournament."""

from __future__ import annotations

import time

from .base import BaseTask


class ArenaTask(BaseTask):
    name = "arena"

    def quick_battles(self, count: int = 5) -> bool:
        """Spend all daily Arena of Heroes tickets (default 5)."""
        self.log(f"running {count} Arena of Heroes battles")
        if not self.nav.goto_arena(self.adb, self.vision):
            return False
        for i in range(count):
            self.popup.dismiss_all(self.adb, self.vision)
            if not self.vision.wait_and_tap(self.adb, "buttons/arena_battle.png", timeout=5):
                break
            time.sleep(1.2)
            # Pick the lowest-rank opponent (bottom slot).
            self.adb.tap(860, 1250)
            time.sleep(1.0)
            self.vision.wait_and_tap(self.adb, "buttons/battle_begin.png", timeout=5)
            # Let the fight auto-complete.
            time.sleep(60)
            self.popup.dismiss_all(self.adb, self.vision)
            self._record("arena_battle", f"{i+1}/{count}")
        # Collect ranking rewards.
        self.vision.wait_and_tap(self.adb, "buttons/collect.png", timeout=3)
        self.popup.dismiss_all(self.adb, self.vision)
        return True

    def challenger(self) -> bool:
        self.log("running Legends' Challenger Tournament")
        if not self.nav.goto_arena(self.adb, self.vision):
            return False
        if not self.vision.wait_and_tap(self.adb, "icons/challenger_icon.png", timeout=5):
            self.log("challenger icon not found")
            return False
        time.sleep(1.0)
        self.vision.wait_and_tap(self.adb, "buttons/challenger_battle.png", timeout=5)
        time.sleep(60)
        self.popup.dismiss_all(self.adb, self.vision)
        return True

    def run(self) -> bool:
        ok = self.quick_battles()
        self.challenger()
        return ok
