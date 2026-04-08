"""Coordinate-first menu navigator for 1080x1920 AFK Arena.

Previously this module used template matching to identify screens and route.
Since the emulator is locked to 1080x1920 we can navigate the entire game
with fixed taps, so this refactor drops template-based routing and uses the
hardcoded coordinates from `bot.coords`.

Template matching is only used by callers for:
    - Victory / Defeat detection (tasks/campaign.py, tasks/tower.py)
    - Popup dismissal (popup_handler.py)
    - Optional pixel-color verification after navigation
"""

from __future__ import annotations

import time

from loguru import logger

from . import coords


class Navigator:
    """Navigate between major screens by tapping known coordinates.

    All methods take `adb` so they can issue taps. `vision` is accepted for
    optional pixel-color verification but is never required.
    """

    def __init__(self, popup_handler) -> None:
        self.popup = popup_handler

    # ------------------------------------------------------------ primitives
    def _nav_tap(self, adb, coord, settle: float = 1.5, vision=None) -> None:
        """Tap a coordinate, sleep for the screen to settle, dismiss popups."""
        self.popup.dismiss_all(adb, vision) if vision else None
        adb.tap(*coord)
        time.sleep(settle)
        if vision:
            self.popup.dismiss_all(adb, vision)

    # ------------------------------------------------------ bottom-nav tabs
    def goto_campaign(self, adb, vision=None) -> bool:
        logger.debug("nav -> campaign")
        self._nav_tap(adb, coords.NAV_CAMPAIGN, vision=vision)
        return True

    def goto_dark_forest(self, adb, vision=None) -> bool:
        logger.debug("nav -> dark_forest")
        self._nav_tap(adb, coords.NAV_DARK_FOREST, vision=vision)
        return True

    def goto_ranhorn(self, adb, vision=None) -> bool:
        logger.debug("nav -> ranhorn")
        self._nav_tap(adb, coords.NAV_RANHORN, vision=vision)
        return True

    def goto_heroes(self, adb, vision=None) -> bool:
        logger.debug("nav -> heroes")
        self._nav_tap(adb, coords.NAV_HEROES, vision=vision)
        return True

    def goto_chat(self, adb, vision=None) -> bool:
        logger.debug("nav -> chat/more")
        self._nav_tap(adb, coords.NAV_CHAT, vision=vision)
        return True

    # ------------------------------------------------------ Ranhorn sub-nav
    def goto_tavern(self, adb, vision=None) -> bool:
        self.goto_ranhorn(adb, vision)
        adb.tap(*coords.RANHORN_NOBLE_TAVERN)
        time.sleep(1.5)
        return True

    def goto_oak_inn(self, adb, vision=None) -> bool:
        self.goto_ranhorn(adb, vision)
        adb.tap(*coords.RANHORN_OAK_INN)
        time.sleep(1.5)
        return True

    def goto_store(self, adb, vision=None) -> bool:
        self.goto_ranhorn(adb, vision)
        adb.tap(*coords.RANHORN_STORE)
        time.sleep(1.5)
        return True

    def goto_guild_hall(self, adb, vision=None) -> bool:
        self.goto_ranhorn(adb, vision)
        adb.tap(*coords.RANHORN_GUILD_HALL)
        time.sleep(1.5)
        return True

    def goto_friends(self, adb, vision=None) -> bool:
        self.goto_ranhorn(adb, vision)
        adb.tap(*coords.RANHORN_FRIENDS_ICON)
        time.sleep(1.5)
        return True

    # -------------------------------------------------- Dark Forest sub-nav
    def goto_kings_tower(self, adb, vision=None) -> bool:
        self.goto_dark_forest(adb, vision)
        adb.tap(*coords.FOREST_KINGS_TOWER)
        time.sleep(1.5)
        return True

    def goto_arena(self, adb, vision=None) -> bool:
        self.goto_dark_forest(adb, vision)
        adb.tap(*coords.FOREST_ARENA)
        time.sleep(1.5)
        return True

    def goto_labyrinth(self, adb, vision=None) -> bool:
        self.goto_dark_forest(adb, vision)
        adb.tap(*coords.FOREST_LABYRINTH)
        time.sleep(1.5)
        return True

    def goto_bounty_board(self, adb, vision=None) -> bool:
        self.goto_dark_forest(adb, vision)
        adb.tap(*coords.FOREST_BOUNTY_BOARD)
        time.sleep(1.5)
        return True

    def goto_challenger(self, adb, vision=None) -> bool:
        self.goto_dark_forest(adb, vision)
        adb.tap(*coords.FOREST_LEGENDS_CHALLENGER)
        time.sleep(1.5)
        return True

    # ----------------------------------------------------------- fallbacks
    def goto_main_menu(self, adb, vision=None, max_attempts: int = 6) -> bool:
        """Mash BACK + dismiss popups until we land on the campaign screen."""
        for _ in range(max_attempts):
            if vision:
                self.popup.dismiss_all(adb, vision)
            adb.tap(*coords.NAV_CAMPAIGN)
            time.sleep(1.2)
            if vision:
                self.popup.dismiss_all(adb, vision)
            return True
        return False
