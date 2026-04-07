"""Reroll automation — create guest account, tutorial, pull, evaluate, repeat."""

from __future__ import annotations

import time

from loguru import logger

from .base import BaseTask
from ..strategy.meta import REROLL_ACCEPTABLE, REDEMPTION_CODES
from .codes import CodesTask


class RerollTask(BaseTask):
    name = "reroll"

    MAX_REROLLS = 30

    def _delete_current_account(self) -> bool:
        self.log("deleting current account")
        self.adb.tap(972, 1820)  # More
        time.sleep(1.0)
        if not self.vision.wait_and_tap(self.adb, "icons/settings_icon.png", timeout=5):
            return False
        if not self.vision.wait_and_tap(self.adb, "buttons/delete_account.png", timeout=5):
            return False
        time.sleep(0.5)
        self.vision.wait_and_tap(self.adb, "buttons/confirm_delete.png", timeout=5)
        time.sleep(5)
        return True

    def _run_tutorial(self) -> bool:
        """Tap-through the tutorial until chapter 1-3 completes."""
        self.log("running tutorial (this takes ~5-10 min)")
        safe_tap = (540, 1700)
        deadline = time.time() + 900  # 15 minute cap
        while time.time() < deadline:
            self.popup.dismiss_all(self.adb, self.vision)
            shot = self.adb.screenshot()
            if self.vision.find(shot, "screens/campaign_map.png", 0.82):
                return True
            # Common tutorial buttons: begin, next, continue.
            for tmpl in ("buttons/battle_begin.png", "buttons/next.png",
                         "buttons/continue.png", "buttons/skip.png"):
                if self.vision.find_and_tap(self.adb, shot, tmpl, 0.82):
                    break
            else:
                # Fall back to safe tap to advance dialogue.
                self.adb.tap(*safe_tap)
            time.sleep(1.2)
        return False

    def _rush_to_4_4(self) -> bool:
        """Auto-push campaign to stage 4-4 to unlock wishlists + free pulls."""
        from .campaign import CampaignTask
        pusher = CampaignTask(
            self.adb, self.vision, self.popup, self.nav, self.state,
            max_retries=5, swap_formation_after=3, give_up_after=80,
        )
        pusher.push()
        return True

    def _set_wishlist(self) -> bool:
        """Open Noble Tavern wishlist and set early-game wishlist heroes."""
        if not self.nav.goto_tavern(self.adb, self.vision):
            return False
        if not self.vision.wait_and_tap(self.adb, "icons/noble_tavern.png", timeout=5):
            return False
        self.vision.wait_and_tap(self.adb, "buttons/wishlist.png", timeout=5)
        # Actual wishlist entries require hero template matches per faction;
        # leave this as a best-effort default wishlist toggle.
        time.sleep(1.0)
        self.vision.wait_and_tap(self.adb, "buttons/confirm.png", timeout=3)
        self.popup.dismiss_all(self.adb, self.vision)
        return True

    def _blow_all_diamonds(self) -> int:
        """Spam 10x pulls until diamonds run out. Returns pull count."""
        from .summon import SummonTask
        summon = SummonTask(self.adb, self.vision, self.popup, self.nav, self.state)
        pulls = 0
        for _ in range(50):
            if not summon.ten_pull_diamonds():
                break
            pulls += 1
        return pulls

    def _got_target_hero(self) -> bool:
        self.nav.goto_heroes(self.adb, self.vision)
        shot = self.adb.screenshot()
        for hero in REROLL_ACCEPTABLE:
            tmpl = f"heroes/{hero.lower()}_portrait.png"
            if self.vision.find(shot, tmpl, 0.84):
                self.log(f"found target hero: {hero}")
                self._record("reroll", f"success: {hero}")
                return True
        return False

    def _single_attempt(self) -> bool:
        if not self._run_tutorial():
            self.log("tutorial failed")
            return False
        self._rush_to_4_4()
        self._set_wishlist()
        CodesTask(self.adb, self.vision, self.popup, self.nav, self.state).enter_codes(REDEMPTION_CODES)
        self._blow_all_diamonds()
        return self._got_target_hero()

    def run(self) -> bool:
        self.log("starting reroll loop")
        for attempt in range(1, self.MAX_REROLLS + 1):
            self.log(f"reroll attempt {attempt}/{self.MAX_REROLLS}")
            try:
                if self._single_attempt():
                    self.log("reroll SUCCESS — linking account recommended")
                    return True
            except Exception as e:
                logger.exception(f"reroll attempt error: {e}")
            self._delete_current_account()
            self.adb.kill_game()
            time.sleep(3)
            self.adb.launch_game()
        self.log("exhausted reroll attempts")
        return False
