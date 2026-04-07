"""Event detection and basic participation (claim free rewards only)."""

from __future__ import annotations

import time

from .base import BaseTask


class EventsTask(BaseTask):
    name = "events"

    def run(self) -> bool:
        self.log("checking events screen for free rewards")
        self.nav.goto_main_menu(self.adb, self.vision)
        if not self.vision.wait_and_tap(self.adb, "icons/events_icon.png", timeout=5):
            return False
        time.sleep(1.0)

        # Iterate through event tabs, claim any collectible rewards.
        for _ in range(12):
            self.popup.dismiss_all(self.adb, self.vision)
            if not self.vision.wait_and_tap(self.adb, "buttons/claim.png", timeout=2):
                break
            time.sleep(0.6)
            self.popup.dismiss_all(self.adb, self.vision)

        self._record("events", "claimed free rewards")
        return True
