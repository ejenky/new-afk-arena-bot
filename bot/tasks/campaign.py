"""Campaign push loop with retry and formation swap logic."""

from __future__ import annotations

import time
from typing import Optional

from loguru import logger

from .base import BaseTask
from ..strategy.formations import formation_for_chapter


class CampaignTask(BaseTask):
    name = "campaign"

    def __init__(self, *args, max_retries: int = 50, swap_formation_after: int = 20,
                 give_up_after: int = 100, wait_hours_on_block: float = 4, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.max_retries = max_retries
        self.swap_formation_after = swap_formation_after
        self.give_up_after = give_up_after
        self.wait_hours_on_block = wait_hours_on_block

    def _wait_for_result(self, timeout: int = 180) -> Optional[str]:
        start = time.time()
        while time.time() - start < timeout:
            screenshot = self.adb.screenshot()
            if self.vision.find(screenshot, "screens/victory.png", 0.82):
                return "victory"
            if self.vision.find(screenshot, "screens/defeat.png", 0.82):
                return "defeat"
            time.sleep(2)
        return None

    def _tap_formation(self, idx: int) -> bool:
        """Tap the idx-th saved formation slot (1-5)."""
        if not self.vision.wait_and_tap(self.adb, "buttons/formations.png", timeout=5):
            return False
        time.sleep(1.0)
        # Formation slot y-coordinates (1080x1920 portrait).
        slot_y = 650 + (idx - 1) * 180
        self.adb.tap(540, slot_y)
        time.sleep(0.6)
        return self.vision.wait_and_tap(self.adb, "buttons/use.png", timeout=5)

    def push(self) -> bool:
        self.log("starting campaign push")
        failures = 0
        total_attempts = 0
        formation_idx = 1
        chapter = self.state.get("current_chapter", 1) if self.state else 1
        plan = formation_for_chapter(chapter)
        self.log(f"formation plan: {plan}")

        while True:
            total_attempts += 1
            if total_attempts >= self.give_up_after:
                self.log(f"give up after {total_attempts} attempts — farming AFK rewards")
                self._record("blocked", f"ch{chapter} after {total_attempts} attempts")
                return False

            self.popup.dismiss_all(self.adb, self.vision)
            self.nav.goto_campaign(self.adb, self.vision)

            if not self.vision.wait_and_tap(self.adb, "buttons/stage_challenge.png", 10):
                self.log("no challenge stage — chapter complete or locked")
                return True

            time.sleep(2)
            self.popup.dismiss_all(self.adb, self.vision)

            if not self.vision.wait_and_tap(self.adb, "buttons/battle_begin.png", 10):
                self.log("no begin button — trying alternative flow")
                continue

            result = self._wait_for_result(timeout=180)
            if result == "victory":
                failures = 0
                time.sleep(3)
                self.popup.dismiss_all(self.adb, self.vision)
                # Tap next / continue safe zone.
                self.adb.tap(540, 1600)
                self._record("victory", f"ch{chapter}")
                if self.state:
                    self.state.set("last_victory_at", time.time())
            elif result == "defeat":
                failures += 1
                self.vision.wait_and_tap(self.adb, "buttons/confirm.png", 10)
                self.log(f"defeat #{failures} (total {total_attempts})")
                if failures >= self.swap_formation_after and formation_idx < len(plan):
                    formation_idx += 1
                    self.log(f"swapping formation -> {plan[formation_idx - 1]}")
                    self._tap_formation(formation_idx)
                    failures = 0
                if failures >= self.max_retries:
                    self.log(f"hit max retries ({self.max_retries}) — pausing")
                    self._record("retry_limit", f"ch{chapter}")
                    return False
            else:
                self.log("unknown battle result — dismissing popups")
                self.popup.dismiss_all(self.adb, self.vision)

    def run(self) -> bool:
        return self.push()
