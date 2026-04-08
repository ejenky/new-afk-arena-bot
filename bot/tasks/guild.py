"""Guild Hunt (Wrizz/Soren) + guild quests — coordinate-driven."""

from __future__ import annotations

import time

from .base import BaseTask
from .. import coords


class GuildTask(BaseTask):
    name = "guild"

    def _dismiss(self) -> None:
        self.popup.dismiss_all(self.adb, self.vision)

    def hunt(self) -> bool:
        self.log("running guild hunt (Wrizz + Soren)")
        self.nav.goto_guild_hall(self.adb, self.vision)
        time.sleep(1.0)
        self._dismiss()
        self.adb.tap(*coords.GUILD_HUNT_ICON)
        time.sleep(1.0)

        for boss_coord in (coords.GUILD_BOSS_WRIZZ, coords.GUILD_BOSS_SOREN):
            self.adb.tap(*boss_coord)
            time.sleep(1.0)
            self.adb.tap(*coords.GUILD_BOSS_CHALLENGE)
            time.sleep(1.0)
            self.adb.tap(*coords.GUILD_BATTLE_BEGIN)
            time.sleep(45)
            self._dismiss()
            self._record("guild_hunt", str(boss_coord))
            self.adb.back()
            time.sleep(1.0)
        return True

    def quests(self) -> bool:
        self.log("collecting guild quest rewards")
        self.nav.goto_guild_hall(self.adb, self.vision)
        time.sleep(1.0)
        self.adb.tap(*coords.GUILD_QUEST_TAB)
        time.sleep(1.0)
        self.adb.tap(*coords.GUILD_QUEST_COLLECT_ALL)
        time.sleep(0.8)
        self._dismiss()
        return True

    def run(self) -> bool:
        ok = self.hunt()
        self.quests()
        return ok
