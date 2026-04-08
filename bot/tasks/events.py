"""Event detection and basic participation — coordinate-driven."""

from __future__ import annotations

import time

from .base import BaseTask
from .. import coords


class EventsTask(BaseTask):
    name = "events"

    def run(self) -> bool:
        self.log("checking events screen for free rewards")
        self.nav.goto_campaign(self.adb, self.vision)
        time.sleep(0.8)
        self.adb.tap(*coords.CAMPAIGN_EVENTS_ICON)
        time.sleep(1.5)

        # Iterate through event tabs (there are usually ~5 visible);
        # in each tab, tap the claim button a few times.
        for _ in range(8):
            self.popup.dismiss_all(self.adb, self.vision)
            self.adb.tap(*coords.EVENTS_CLAIM_BUTTON)
            time.sleep(0.6)
            self.popup.dismiss_all(self.adb, self.vision)

        self._record("events", "claimed free rewards")
        self.adb.back()
        return True
