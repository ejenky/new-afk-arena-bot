"""Redemption code entry — coordinate-driven."""

from __future__ import annotations

import time
from typing import Iterable

from .base import BaseTask
from .. import coords
from ..strategy.meta import REDEMPTION_CODES


class CodesTask(BaseTask):
    name = "codes"

    def _open_redemption_screen(self) -> bool:
        # More tab -> Settings -> Redemption code.
        self.nav.goto_chat(self.adb, self.vision)
        time.sleep(1.0)
        self.adb.tap(*coords.MORE_MENU_SETTINGS)
        time.sleep(1.2)
        self.adb.tap(*coords.SETTINGS_REDEEM_CODE)
        time.sleep(1.2)
        return True

    def enter_codes(self, codes_list: Iterable[str] = REDEMPTION_CODES) -> int:
        self.log("entering redemption codes")
        if not self._open_redemption_screen():
            return 0

        entered = 0
        for code in codes_list:
            self.adb.tap(*coords.CODE_INPUT_FIELD)
            time.sleep(0.4)
            self.adb.text_input(code)
            time.sleep(0.4)
            self.adb.tap(*coords.CODE_REDEEM_BUTTON)
            time.sleep(1.0)
            entered += 1
            self.log(f"redeemed: {code}")
            self._record("code", code)
            self.popup.dismiss_all(self.adb, self.vision)
            time.sleep(0.8)
        return entered

    def run(self) -> bool:
        self.enter_codes()
        return True
