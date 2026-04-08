"""Daily task loop — all 15 dailies driven by hardcoded 1080x1920 coordinates.

After the coordinate-first refactor, this module navigates entirely via
`bot.coords` taps. Template matching is only used inside popup_handler for
safe dismissal. If a specific tap misses, use `python cli.py daily --debug`
to get before/after screenshots with red crosshairs.
"""

from __future__ import annotations

import time

from .base import BaseTask
from .. import coords
from ..strategy.resource_rules import DAILY_TASK_ORDER


class DailyTask(BaseTask):
    name = "daily"

    def _dismiss(self) -> None:
        self.popup.dismiss_all(self.adb, self.vision)

    # ---------------------------------------------------- individual dailies
    def collect_afk_rewards(self) -> None:
        self.nav.goto_campaign(self.adb, self.vision)
        self.adb.tap(*coords.CAMPAIGN_AFK_CHEST)
        time.sleep(1.5)
        self.adb.tap(*coords.CAMPAIGN_COLLECT_AFK)
        time.sleep(1.0)
        self._dismiss()
        # Close the chest panel.
        self.adb.tap(*coords.CAMPAIGN_CHEST_CLOSE)
        time.sleep(0.6)
        self._dismiss()

    def claim_fast_rewards(self) -> None:
        self.nav.goto_campaign(self.adb, self.vision)
        self.adb.tap(*coords.CAMPAIGN_AFK_CHEST)
        time.sleep(1.2)
        self.adb.tap(*coords.CAMPAIGN_FAST_REWARDS)
        time.sleep(1.0)
        self.adb.tap(*coords.CAMPAIGN_FAST_REWARDS_FREE)
        time.sleep(0.8)
        self._dismiss()
        self.adb.tap(*coords.CAMPAIGN_CHEST_CLOSE)
        time.sleep(0.6)
        self._dismiss()

    def claim_daily_gift(self) -> None:
        self.nav.goto_oak_inn(self.adb, self.vision)
        self.adb.tap(*coords.OAK_INN_GIFT)
        time.sleep(1.0)
        self.adb.tap(*coords.OAK_INN_CLAIM)
        time.sleep(0.8)
        self._dismiss()

    def send_receive_companion(self) -> None:
        self.nav.goto_friends(self.adb, self.vision)
        self.adb.tap(*coords.FRIENDS_SEND_ALL)
        time.sleep(0.6)
        self.adb.tap(*coords.FRIENDS_RECEIVE_ALL)
        time.sleep(0.8)
        self._dismiss()
        self.adb.tap(*coords.FRIENDS_CLOSE)
        time.sleep(0.5)

    def collect_mail(self) -> None:
        self.nav.goto_campaign(self.adb, self.vision)
        self.adb.tap(*coords.CAMPAIGN_MAIL_ICON)
        time.sleep(1.2)
        self.adb.tap(*coords.MAIL_COLLECT_ALL)
        time.sleep(0.8)
        self._dismiss()
        self.adb.tap(*coords.MAIL_CLOSE)
        time.sleep(0.5)

    def level_hero(self) -> None:
        from .level_heroes import LevelHeroesTask
        LevelHeroesTask(self.adb, self.vision, self.popup, self.nav, self.state).quick_level()

    def enhance_gear(self) -> None:
        self.nav.goto_heroes(self.adb, self.vision)
        self.adb.tap(*coords.HEROES_FIRST_PORTRAIT)
        time.sleep(1.0)
        self.adb.tap(*coords.HERO_ENHANCE_GEAR)
        time.sleep(0.8)
        self._dismiss()
        self.adb.back()

    def guild_hunt(self) -> None:
        from .guild import GuildTask
        GuildTask(self.adb, self.vision, self.popup, self.nav, self.state).hunt()

    def arena_battles(self) -> None:
        from .arena import ArenaTask
        ArenaTask(self.adb, self.vision, self.popup, self.nav, self.state).quick_battles()

    def challenger_tournament(self) -> None:
        from .arena import ArenaTask
        ArenaTask(self.adb, self.vision, self.popup, self.nav, self.state).challenger()

    def kings_tower_attempt(self) -> None:
        from .tower import TowerTask
        TowerTask(self.adb, self.vision, self.popup, self.nav, self.state).kings_tower(max_attempts=3)

    def summon_hero(self) -> None:
        from .summon import SummonTask
        SummonTask(self.adb, self.vision, self.popup, self.nav, self.state).single_free()

    def bounty_board(self) -> None:
        from .bounty import BountyTask
        BountyTask(self.adb, self.vision, self.popup, self.nav, self.state).run()

    def collect_daily_quest_reward(self) -> None:
        self.nav.goto_campaign(self.adb, self.vision)
        self.adb.tap(*coords.CAMPAIGN_QUEST_ICON)
        time.sleep(1.2)
        # Tap down the quest list claiming each reward slot.
        for y in coords.QUEST_CLAIM_LINE_Y:
            self.adb.tap(coords.QUEST_CLAIM_X, y)
            time.sleep(0.3)
        self._dismiss()
        self.adb.back()

    def store_purchases(self) -> None:
        from .store import StoreTask
        StoreTask(self.adb, self.vision, self.popup, self.nav, self.state).run()

    # ------------------------------------------------------------------ run
    def run(self) -> bool:
        self.log("starting daily task loop (coordinate-driven)")
        for task_name in DAILY_TASK_ORDER:
            method = getattr(self, task_name, None)
            if method is None:
                self.log(f"skip missing daily: {task_name}")
                continue
            try:
                self.log(f"-> {task_name}")
                method()
                self._record(f"daily:{task_name}", "ok")
            except Exception as e:
                self.log(f"daily {task_name} failed: {e}")
                self._record(f"daily:{task_name}", f"error: {e}")
                self._dismiss()
                self.nav.goto_main_menu(self.adb, self.vision)
        self.log("daily task loop complete")
        return True
