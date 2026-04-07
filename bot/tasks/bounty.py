"""Bounty Board — dispatch daily bounties and collect rewards."""

from __future__ import annotations

import time

from .base import BaseTask


class BountyTask(BaseTask):
    name = "bounty"

    def run(self) -> bool:
        self.log("running bounty board")
        if not self.nav.goto_bounty_board(self.adb, self.vision):
            return False
        self.popup.dismiss_all(self.adb, self.vision)

        # Collect any completed bounties first.
        self.vision.wait_and_tap(self.adb, "buttons/collect_all.png", timeout=3)
        self.popup.dismiss_all(self.adb, self.vision)

        # Dispatch as many bounties as possible with "Auto Dispatch".
        for _ in range(10):
            if not self.vision.wait_and_tap(self.adb, "buttons/auto_dispatch.png", timeout=3):
                break
            time.sleep(0.8)
            self.vision.wait_and_tap(self.adb, "buttons/confirm.png", timeout=3)
            self.popup.dismiss_all(self.adb, self.vision)

        self._record("bounty", "ok")
        return True
