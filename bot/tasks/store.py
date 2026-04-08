"""Store purchasing — coordinate-driven, blacklist-protected.

Without item-specific templates we can't identify individual items, so this
task taps known-safe slot positions and relies on the popup handler's
PURCHASE_BLACKLIST to block any unexpected diamond confirmations.

Safe targets by shop row (at 1080x1920):
    Row 1 — gold items only: Hero Essence x2, POE Coins
    Row 2 — gold + 5x Elite Soulstones (safe: 90 diamonds)
    Row 3 — diamond-cost items (skipped unless late_game)

The purchase_blacklist in bot/popup_handler.py will press BACK instead of
tapping "Confirm" on any dialog that shows a diamond cost we didn't expect.
"""

from __future__ import annotations

import time

from .base import BaseTask
from .. import coords
from ..strategy.progression import detect_phase, Phase


class StoreTask(BaseTask):
    name = "store"

    # Slot indices (0-based) for known daily purchases.
    GOLD_SLOTS = [0, 1, 2]        # Row 1 — all gold (essence + POE)
    SOULSTONE_SLOT = 3            # Row 2 slot 0 — 5x Elite Soulstones (90 diamonds)
    LATE_GAME_SLOTS = [3, 4, 5]   # Row 2 — dust / EXP crates once in phase 3

    def _dismiss(self) -> None:
        self.popup.dismiss_all(self.adb, self.vision)

    def _buy_slot(self, slot_index: int) -> bool:
        """Tap a shop slot and confirm the purchase.

        The popup blacklist blocks any unexpected diamond cost dialogs; see
        bot/popup_handler.py PURCHASE_BLACKLIST.
        """
        if slot_index >= len(coords.STORE_SLOTS):
            return False
        x, y = coords.STORE_SLOTS[slot_index]
        self.adb.tap(x, y)
        time.sleep(0.8)
        self.adb.tap(*coords.STORE_BUY_BUTTON)
        time.sleep(0.6)
        # Any surprise diamond dialog is caught here and BACK is pressed.
        dismissed = self.popup.dismiss_all(self.adb, self.vision, max_attempts=2)
        if dismissed:
            self._record("store", f"slot {slot_index} -> dismissed dialog")
            return False
        self._record("store", f"slot {slot_index} ok")
        return True

    def run(self) -> bool:
        self.log("running store purchases (coord-driven)")
        self.nav.goto_store(self.adb, self.vision)
        time.sleep(1.5)
        self._dismiss()

        # Gold-only row.
        for idx in self.GOLD_SLOTS:
            self._buy_slot(idx)

        # 5x Elite Soulstones (safe 90 diamond spend).
        self._buy_slot(self.SOULSTONE_SLOT)

        chapter = self.state.get("current_chapter", 1) if self.state else 1
        if detect_phase(chapter) is Phase.LATE:
            self.log("phase 3 — buying dust/EXP crates")
            for idx in self.LATE_GAME_SLOTS:
                self._buy_slot(idx)

        self._dismiss()
        return True
