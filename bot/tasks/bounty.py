"""Bounty Board — coordinate-driven dispatch and collection."""

from __future__ import annotations

import time

from .base import BaseTask
from .. import coords


class BountyTask(BaseTask):
    name = "bounty"

    def _dismiss(self) -> None:
        self.popup.dismiss_all(self.adb, self.vision)

    def run(self) -> bool:
        self.log("running bounty board")
        self.nav.goto_bounty_board(self.adb, self.vision)
        time.sleep(1.0)
        self._dismiss()

        # Collect completed bounties first.
        self.adb.tap(*coords.BOUNTY_COLLECT_ALL)
        time.sleep(0.8)
        self._dismiss()

        # Auto-dispatch loop — tap, confirm, dismiss, repeat.
        for _ in range(10):
            self.adb.tap(*coords.BOUNTY_AUTO_DISPATCH)
            time.sleep(0.8)
            self.adb.tap(*coords.BOUNTY_DISPATCH_CONFIRM)
            time.sleep(0.6)
            self._dismiss()

        self._record("bounty", "ok")
        return True
