"""Daily task loop — execute all 15 dailies for 100 activity points."""

from __future__ import annotations

import time

from .base import BaseTask
from ..strategy.resource_rules import DAILY_TASK_ORDER


class DailyTask(BaseTask):
    name = "daily"

    # ---------------------------------------------------- individual dailies
    def collect_afk_rewards(self) -> None:
        self.nav.goto_campaign(self.adb, self.vision)
        # AFK rewards chest sits bottom-center on campaign screen.
        self.adb.tap(540, 1420)
        time.sleep(1.5)
        self.vision.wait_and_tap(self.adb, "buttons/collect.png", timeout=5)
        self.popup.dismiss_all(self.adb, self.vision)

    def claim_fast_rewards(self) -> None:
        self.nav.goto_campaign(self.adb, self.vision)
        self.adb.tap(540, 1420)
        time.sleep(1.0)
        self.vision.wait_and_tap(self.adb, "buttons/fast_rewards.png", timeout=5)
        time.sleep(1.0)
        self.vision.wait_and_tap(self.adb, "buttons/free_collect.png", timeout=5)
        self.popup.dismiss_all(self.adb, self.vision)

    def claim_daily_gift(self) -> None:
        self.nav.goto_ranhorn(self.adb, self.vision)
        self.vision.wait_and_tap(self.adb, "icons/oak_inn_icon.png", timeout=5)
        time.sleep(1.0)
        self.vision.wait_and_tap(self.adb, "buttons/claim_gift.png", timeout=5)
        self.popup.dismiss_all(self.adb, self.vision)

    def send_receive_companion(self) -> None:
        self.nav.goto_ranhorn(self.adb, self.vision)
        self.vision.wait_and_tap(self.adb, "icons/friends_icon.png", timeout=5)
        time.sleep(1.0)
        self.vision.wait_and_tap(self.adb, "buttons/send_all.png", timeout=5)
        self.vision.wait_and_tap(self.adb, "buttons/receive_all.png", timeout=5)
        self.popup.dismiss_all(self.adb, self.vision)

    def collect_mail(self) -> None:
        self.nav.goto_campaign(self.adb, self.vision)
        self.vision.wait_and_tap(self.adb, "icons/mail_icon.png", timeout=5)
        time.sleep(1.0)
        self.vision.wait_and_tap(self.adb, "buttons/collect_all.png", timeout=5)
        self.popup.dismiss_all(self.adb, self.vision)

    def level_hero(self) -> None:
        # Route via hero leveling task.
        from .level_heroes import LevelHeroesTask
        LevelHeroesTask(self.adb, self.vision, self.popup, self.nav, self.state).quick_level()

    def enhance_gear(self) -> None:
        self.nav.goto_heroes(self.adb, self.vision)
        self.vision.wait_and_tap(self.adb, "buttons/enhance_gear.png", timeout=5)
        self.popup.dismiss_all(self.adb, self.vision)

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
        self.vision.wait_and_tap(self.adb, "icons/quest_icon.png", timeout=5)
        time.sleep(1.0)
        # Claim everything visible.
        for _ in range(10):
            if not self.vision.wait_and_tap(self.adb, "buttons/collect.png", timeout=2):
                break
            self.popup.dismiss_all(self.adb, self.vision)

    def store_purchases(self) -> None:
        from .store import StoreTask
        StoreTask(self.adb, self.vision, self.popup, self.nav, self.state).run()

    # ------------------------------------------------------------------ run
    def run(self) -> bool:
        self.log("starting daily task loop")
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
                # Attempt to recover by dismissing popups and backing out.
                self.popup.dismiss_all(self.adb, self.vision)
                self.nav.goto_main_menu(self.adb, self.vision)
        self.log("daily task loop complete")
        return True
