"""Redemption code entry."""

from __future__ import annotations

import time
from typing import Iterable

from .base import BaseTask
from ..strategy.meta import REDEMPTION_CODES


class CodesTask(BaseTask):
    name = "codes"

    def _open_redemption_screen(self) -> bool:
        # Main menu -> settings -> redemption code.
        self.adb.tap(*(972, 1820))  # "More" bottom-right.
        time.sleep(1.0)
        if not self.vision.wait_and_tap(self.adb, "icons/settings_icon.png", timeout=5):
            return False
        time.sleep(1.0)
        return self.vision.wait_and_tap(self.adb, "buttons/redeem_code.png", timeout=5)

    def enter_codes(self, codes: Iterable[str] = REDEMPTION_CODES) -> int:
        self.log("entering redemption codes")
        if not self._open_redemption_screen():
            self.log("could not open redemption screen")
            return 0

        entered = 0
        for code in codes:
            if not self.vision.wait_and_tap(self.adb, "icons/code_input_field.png", timeout=5):
                continue
            time.sleep(0.3)
            self.adb.text_input(code)
            time.sleep(0.3)
            if self.vision.wait_and_tap(self.adb, "buttons/redeem.png", timeout=3):
                entered += 1
                self.log(f"redeemed: {code}")
                self._record("code", code)
            self.popup.dismiss_all(self.adb, self.vision)
            time.sleep(1.0)
        return entered

    def run(self) -> bool:
        self.enter_codes()
        return True
