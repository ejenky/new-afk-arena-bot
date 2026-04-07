"""Store purchasing — strictly rule-based, blacklist-protected."""

from __future__ import annotations

import time

from .base import BaseTask
from ..strategy.resource_rules import STORE_BUY_RULES


# Templates for items we're allowed to buy. If a template doesn't exist, the
# item is silently skipped — no blind taps.
GOLD_ITEMS = [
    "store/hero_essence.png",
    "store/poe_coin.png",
]

DIAMOND_ITEMS = [
    "store/elite_soulstone_5x.png",
    "store/dust_crate.png",   # Phase 3 only — caller should gate
    "store/exp_crate.png",    # Phase 3 only
]


class StoreTask(BaseTask):
    name = "store"

    def _buy_all_matching(self, template: str, max_buys: int = 10) -> int:
        bought = 0
        for _ in range(max_buys):
            shot = self.adb.screenshot()
            match = self.vision.find(shot, template, 0.85)
            if not match:
                break
            self.adb.tap(match[0], match[1])
            time.sleep(0.8)
            # Tap "Buy" in the purchase confirmation dialog — ONLY if this was
            # triggered via an allowed item template. The popup blacklist in
            # PopupHandler prevents any diamond-cost confirmation from slipping
            # in via another path.
            if self.vision.wait_and_tap(self.adb, "buttons/buy.png", timeout=3):
                bought += 1
            self.popup.dismiss_all(self.adb, self.vision)
        return bought

    def buy_gold_items(self) -> None:
        for item in GOLD_ITEMS:
            count = self._buy_all_matching(item)
            if count:
                self.log(f"bought {count}x {item}")
                self._record("store", f"{item} x{count}")

    def buy_diamond_items(self, late_game: bool = False) -> None:
        # Always safe: 5x Elite Soulstones for 90 diamonds.
        count = self._buy_all_matching("store/elite_soulstone_5x.png", max_buys=1)
        if count:
            self._record("store", f"elite_soulstone_5x x{count}")
        # Dust and EXP crates only in Phase 3 (RC Cramming).
        if late_game:
            for item in ("store/dust_crate.png", "store/exp_crate.png"):
                count = self._buy_all_matching(item, max_buys=10)
                if count:
                    self._record("store", f"{item} x{count}")

    def run(self) -> bool:
        self.log("running store purchases")
        if not self.nav.goto_store(self.adb, self.vision):
            return False
        self.popup.dismiss_all(self.adb, self.vision)

        chapter = self.state.get("current_chapter", 1) if self.state else 1
        late_game = chapter >= 26

        self.buy_gold_items()
        self.buy_diamond_items(late_game=late_game)
        self.popup.dismiss_all(self.adb, self.vision)
        return True
