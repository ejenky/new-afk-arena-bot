"""Campaign push loop with retry and formation swap logic.

Coordinate-driven navigation and button taps. Template matching is retained
ONLY for Victory / Defeat banner detection after each battle — we genuinely
need to see the pixels to know the outcome.
"""

from __future__ import annotations

import time
from typing import Optional

from loguru import logger

from .base import BaseTask
from .. import coords
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

    def _dismiss(self) -> None:
        self.popup.dismiss_all(self.adb, self.vision)

    def _wait_for_result(self, timeout: int = 180) -> Optional[str]:
        """Watch for the Victory / Defeat banner template.

        This is the one place in the campaign loop that still uses template
        matching — the battle outcome can't be inferred from a fixed pixel.
        """
        start = time.time()
        while time.time() - start < timeout:
            screenshot = self.adb.screenshot()
            if self.vision.find(screenshot, "screens/victory.png", 0.70):
                return "victory"
            if self.vision.find(screenshot, "screens/defeat.png", 0.70):
                return "defeat"
            time.sleep(2)
        return None

    def _swap_formation(self, slot: int) -> None:
        """Switch to the Nth saved formation (1-5)."""
        if slot < 1 or slot > len(coords.FORMATION_SLOTS):
            return
        self.adb.tap(*coords.FORMATION_BUTTON)
        time.sleep(1.0)
        self.adb.tap(*coords.FORMATION_SLOTS[slot - 1])
        time.sleep(0.6)
        self.adb.tap(*coords.FORMATION_USE_BUTTON)
        time.sleep(0.6)
        self._dismiss()

    def push(self) -> bool:
        self.log("starting campaign push (coord-driven)")
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

            self._dismiss()
            self.nav.goto_campaign(self.adb, self.vision)
            time.sleep(0.8)
            self._dismiss()

            # Tap the stage marker to open the battle prep screen.
            self.adb.tap(*coords.CAMPAIGN_STAGE_MARKER)
            time.sleep(1.2)
            self._dismiss()

            # Begin battle.
            self.adb.tap(*coords.CAMPAIGN_BEGIN_BATTLE)

            result = self._wait_for_result(timeout=180)
            if result == "victory":
                failures = 0
                time.sleep(3)
                self._dismiss()
                self.adb.tap(*coords.BATTLE_CONTINUE)
                self._record("victory", f"ch{chapter}")
                if self.state:
                    self.state.set("last_victory_at", time.time())
            elif result == "defeat":
                failures += 1
                self.adb.tap(*coords.BATTLE_RETRY)
                self.log(f"defeat #{failures} (total {total_attempts})")
                if failures >= self.swap_formation_after and formation_idx < len(plan):
                    formation_idx += 1
                    self.log(f"swapping formation -> {plan[formation_idx - 1]}")
                    self._swap_formation(formation_idx)
                    failures = 0
                if failures >= self.max_retries:
                    self.log(f"hit max retries ({self.max_retries}) — pausing")
                    self._record("retry_limit", f"ch{chapter}")
                    return False
            else:
                self.log("unknown battle result — dismissing popups")
                self._dismiss()

    def run(self) -> bool:
        return self.push()
