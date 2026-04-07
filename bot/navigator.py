"""Screen detection and menu navigation state machine.

Each known screen has an identifier template. The navigator uses these to
detect the current screen and walk the menu graph back to the main menu,
from which it can reach any other screen.
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Dict, Optional, Tuple

from loguru import logger


class Screen(str, Enum):
    UNKNOWN = "unknown"
    MAIN_MENU = "main_menu"
    CAMPAIGN_MAP = "campaign_map"
    DARK_FOREST = "dark_forest"
    RANHORN = "ranhorn"
    TAVERN = "tavern"
    STORE = "store"
    ARENA = "arena"
    KINGS_TOWER = "kings_tower"
    BOUNTY_BOARD = "bounty_board"
    LABYRINTH = "labyrinth"
    GUILD_HALL = "guild_hall"
    HEROES = "heroes"
    VICTORY = "victory"
    DEFEAT = "defeat"


# Templates used to identify each screen.
SCREEN_IDENTIFIERS: Dict[Screen, str] = {
    Screen.MAIN_MENU: "screens/main_menu.png",
    Screen.CAMPAIGN_MAP: "screens/campaign_map.png",
    Screen.DARK_FOREST: "screens/dark_forest.png",
    Screen.RANHORN: "screens/ranhorn.png",
    Screen.TAVERN: "screens/tavern.png",
    Screen.STORE: "screens/store.png",
    Screen.ARENA: "screens/arena.png",
    Screen.KINGS_TOWER: "screens/kings_tower.png",
    Screen.BOUNTY_BOARD: "screens/bounty_board.png",
    Screen.LABYRINTH: "screens/labyrinth.png",
    Screen.GUILD_HALL: "screens/guild_hall.png",
    Screen.HEROES: "screens/heroes.png",
    Screen.VICTORY: "screens/victory.png",
    Screen.DEFEAT: "screens/defeat.png",
}

# Bottom-nav tap coordinates for 1080x1920 portrait.
BOTTOM_NAV: Dict[Screen, Tuple[int, int]] = {
    Screen.RANHORN:      (108, 1820),
    Screen.DARK_FOREST:  (324, 1820),
    Screen.CAMPAIGN_MAP: (540, 1820),
    Screen.HEROES:       (756, 1820),
    Screen.MAIN_MENU:    (972, 1820),  # "More"/main
}


class Navigator:
    def __init__(self, popup_handler) -> None:
        self.popup = popup_handler

    # ------------------------------------------------------------- detection
    def detect_screen(self, adb, vision) -> Screen:
        screenshot = adb.screenshot()
        for screen, template in SCREEN_IDENTIFIERS.items():
            if not vision.template_exists(template):
                continue
            if vision.find(screenshot, template, confidence=0.82):
                logger.debug(f"detect_screen -> {screen.value}")
                return screen
        return Screen.UNKNOWN

    # ---------------------------------------------------------- "home" reset
    def goto_main_menu(self, adb, vision, max_attempts: int = 10) -> bool:
        """Try to reach campaign/main menu by dismissing popups and pressing back."""
        for _ in range(max_attempts):
            self.popup.dismiss_all(adb, vision)
            screen = self.detect_screen(adb, vision)
            if screen == Screen.CAMPAIGN_MAP or screen == Screen.MAIN_MENU:
                return True
            if screen == Screen.UNKNOWN:
                adb.back()
            else:
                # Tap campaign bottom-nav.
                adb.tap(*BOTTOM_NAV[Screen.CAMPAIGN_MAP])
            time.sleep(1.5)
        logger.warning("goto_main_menu: failed to reach main menu")
        return False

    # ---------------------------------------------------------------- routes
    def goto_campaign(self, adb, vision) -> bool:
        self.popup.dismiss_all(adb, vision)
        adb.tap(*BOTTOM_NAV[Screen.CAMPAIGN_MAP])
        time.sleep(1.5)
        self.popup.dismiss_all(adb, vision)
        return True

    def goto_dark_forest(self, adb, vision) -> bool:
        self.popup.dismiss_all(adb, vision)
        adb.tap(*BOTTOM_NAV[Screen.DARK_FOREST])
        time.sleep(1.5)
        self.popup.dismiss_all(adb, vision)
        return self.detect_screen(adb, vision) == Screen.DARK_FOREST

    def goto_ranhorn(self, adb, vision) -> bool:
        self.popup.dismiss_all(adb, vision)
        adb.tap(*BOTTOM_NAV[Screen.RANHORN])
        time.sleep(1.5)
        self.popup.dismiss_all(adb, vision)
        return self.detect_screen(adb, vision) == Screen.RANHORN

    def goto_heroes(self, adb, vision) -> bool:
        self.popup.dismiss_all(adb, vision)
        adb.tap(*BOTTOM_NAV[Screen.HEROES])
        time.sleep(1.5)
        self.popup.dismiss_all(adb, vision)
        return self.detect_screen(adb, vision) == Screen.HEROES

    # ------------------------------------------------ sub-screens via icons
    def goto_tavern(self, adb, vision) -> bool:
        if not self.goto_ranhorn(adb, vision):
            return False
        return vision.wait_and_tap(adb, "icons/tavern_icon.png", timeout=5)

    def goto_store(self, adb, vision) -> bool:
        if not self.goto_ranhorn(adb, vision):
            return False
        return vision.wait_and_tap(adb, "icons/store_icon.png", timeout=5)

    def goto_guild_hall(self, adb, vision) -> bool:
        if not self.goto_ranhorn(adb, vision):
            return False
        return vision.wait_and_tap(adb, "icons/guild_hall_icon.png", timeout=5)

    def goto_kings_tower(self, adb, vision) -> bool:
        if not self.goto_dark_forest(adb, vision):
            return False
        return vision.wait_and_tap(adb, "icons/kings_tower_icon.png", timeout=5)

    def goto_arena(self, adb, vision) -> bool:
        if not self.goto_dark_forest(adb, vision):
            return False
        return vision.wait_and_tap(adb, "icons/arena_icon.png", timeout=5)

    def goto_labyrinth(self, adb, vision) -> bool:
        if not self.goto_dark_forest(adb, vision):
            return False
        return vision.wait_and_tap(adb, "icons/labyrinth_icon.png", timeout=5)

    def goto_bounty_board(self, adb, vision) -> bool:
        if not self.goto_dark_forest(adb, vision):
            return False
        return vision.wait_and_tap(adb, "icons/bounty_board_icon.png", timeout=5)
