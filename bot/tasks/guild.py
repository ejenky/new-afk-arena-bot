"""Guild Hunt (Wrizz/Soren) + guild quests."""

from __future__ import annotations

import time

from .base import BaseTask


class GuildTask(BaseTask):
    name = "guild"

    def hunt(self) -> bool:
        self.log("running guild hunt (Wrizz + Soren)")
        if not self.nav.goto_guild_hall(self.adb, self.vision):
            return False
        self.popup.dismiss_all(self.adb, self.vision)

        if not self.vision.wait_and_tap(self.adb, "icons/guild_hunt.png", timeout=5):
            self.log("guild hunt icon not found")
            return False
        time.sleep(1.0)

        for boss in ("wrizz", "soren"):
            boss_tmpl = f"icons/guild_boss_{boss}.png"
            if not self.vision.wait_and_tap(self.adb, boss_tmpl, timeout=3):
                continue
            time.sleep(1.0)
            self.vision.wait_and_tap(self.adb, "buttons/challenge.png", timeout=5)
            time.sleep(1.0)
            # Start battle + auto.
            self.vision.wait_and_tap(self.adb, "buttons/battle_begin.png", timeout=5)
            time.sleep(45)
            self.popup.dismiss_all(self.adb, self.vision)
            self._record("guild_hunt", boss)
            self.adb.back()
            time.sleep(1.0)
        return True

    def quests(self) -> bool:
        self.log("collecting guild quest rewards")
        if not self.nav.goto_guild_hall(self.adb, self.vision):
            return False
        self.vision.wait_and_tap(self.adb, "icons/guild_quest.png", timeout=5)
        self.vision.wait_and_tap(self.adb, "buttons/collect_all.png", timeout=5)
        self.popup.dismiss_all(self.adb, self.vision)
        return True

    def run(self) -> bool:
        ok = self.hunt()
        self.quests()
        return ok
