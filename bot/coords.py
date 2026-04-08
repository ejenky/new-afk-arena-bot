"""Hardcoded coordinate map for AFK Arena at 1080x1920 portrait.

Inspired by the coordinate-based approach in Fortigate/AutoAFK and
zebscripts/AFK-Daily. Because the emulator is locked to 1080x1920, we can
navigate the entire game with fixed taps and only fall back to template
matching for things we genuinely need to see the pixels for:

    - Victory / Defeat banners after a battle
    - Popup dismissal (the universal popup handler)
    - Optional pixel-color screen verification

All coordinates are given as (x, y) tuples in the 1080x1920 coordinate space.
Everything marked `APPROX` is a best-effort estimate — tune against your
emulator if taps miss. The best way to verify is `python cli.py daily --debug`
which saves before/after screenshots for every tap with a red crosshair.
"""

from __future__ import annotations

from typing import Tuple

Coord = Tuple[int, int]
Color = Tuple[int, int, int]  # RGB


# =============================================================================
# Screen dimensions
# =============================================================================
SCREEN_W = 1080
SCREEN_H = 1920

CENTER_X = SCREEN_W // 2  # 540


# =============================================================================
# Bottom navigation bar — always visible on main screens
# =============================================================================
NAV_Y = 1850

NAV_RANHORN:     Coord = (108, NAV_Y)
NAV_DARK_FOREST: Coord = (324, NAV_Y)
NAV_CAMPAIGN:    Coord = (540, NAV_Y)
NAV_HEROES:      Coord = (760, NAV_Y)
NAV_CHAT:        Coord = (972, NAV_Y)

# Safe tap zones — used to dismiss "tap anywhere to continue" dialogs.
SAFE_TAP_TOP:    Coord = (540, 200)
SAFE_TAP_BOTTOM: Coord = (540, 1700)


# =============================================================================
# Universal buttons (positions common across dialogs)
# =============================================================================
BTN_CONFIRM:         Coord = (660, 1200)   # Center-right confirm in 2-button dialogs
BTN_CANCEL:          Coord = (420, 1200)
BTN_CONFIRM_CENTER:  Coord = (540, 1200)   # Single-button "OK"
BTN_CLOSE_X_TR:      Coord = (940, 240)    # Close (X) top-right
BTN_BACK_ARROW:      Coord = (60, 100)     # Back arrow top-left


# =============================================================================
# Campaign screen
# =============================================================================
# AFK chest / reward panel in bottom-center of campaign map.
CAMPAIGN_AFK_CHEST:          Coord = (540, 1420)
# The chest popup buttons:
CAMPAIGN_COLLECT_AFK:        Coord = (540, 1150)  # "Collect" button inside AFK panel
CAMPAIGN_FAST_REWARDS:       Coord = (810, 1150)  # "Fast Rewards" (bottom-right of AFK panel)
CAMPAIGN_FAST_REWARDS_FREE:  Coord = (540, 1050)  # Free fast reward button
CAMPAIGN_CHEST_CLOSE:        Coord = (540, 1700)  # Safe-tap to close chest popup

# Top-right floating icons.
CAMPAIGN_MAIL_ICON:          Coord = (960, 260)
CAMPAIGN_QUEST_ICON:         Coord = (960, 400)
CAMPAIGN_EVENTS_ICON:        Coord = (960, 560)

# Begin battle on campaign map (progression stage).
CAMPAIGN_BEGIN_BATTLE:       Coord = (540, 1700)
CAMPAIGN_STAGE_MARKER:       Coord = (540, 1000)  # Approx center of stage card

# Formation picker
FORMATION_BUTTON:            Coord = (200, 1700)  # Bottom-left on battle screen
FORMATION_SLOTS = [                               # 5 save slots on formation picker
    (540, 650),
    (540, 830),
    (540, 1010),
    (540, 1190),
    (540, 1370),
]
FORMATION_USE_BUTTON:        Coord = (540, 1700)


# =============================================================================
# Mail / Quest / Event panels
# =============================================================================
MAIL_COLLECT_ALL:            Coord = (540, 1700)
MAIL_CLOSE:                  Coord = (940, 260)

QUEST_CLAIM_ALL:             Coord = (900, 500)   # First collectable quest reward
QUEST_CLAIM_LINE_Y = [500, 660, 820, 980, 1140, 1300, 1460, 1620]
QUEST_CLAIM_X = 900

EVENTS_CLAIM_BUTTON:         Coord = (900, 1300)  # Generic "Claim" inside events


# =============================================================================
# Ranhorn buildings (Ranhorn is accessed via NAV_RANHORN)
# =============================================================================
# APPROX — verify against your emulator and tune as needed.
RANHORN_NOBLE_TAVERN:        Coord = (570, 1100)
RANHORN_OAK_INN:             Coord = (820, 700)
RANHORN_GUILD_HALL:          Coord = (230, 1200)
RANHORN_STORE:               Coord = (860, 1420)
RANHORN_FRIENDS_ICON:        Coord = (540, 310)
RANHORN_CHAMPIONSHIP:        Coord = (260, 800)


# =============================================================================
# Noble Tavern (summoning)
# =============================================================================
TAVERN_NOBLE_ENTRY:          Coord = (540, 900)
TAVERN_ALL_HERO_TAB:         Coord = (360, 1550)
TAVERN_FACTION_TAB:          Coord = (720, 1550)

TAVERN_SUMMON_1X:            Coord = (400, 1720)
TAVERN_SUMMON_10X:           Coord = (720, 1720)
TAVERN_FREE_SUMMON:          Coord = (540, 1430)
TAVERN_FREE_COLLECT:         Coord = (540, 1700)

TAVERN_WISHLIST_BUTTON:      Coord = (960, 1700)


# =============================================================================
# Oak Inn (daily gift)
# =============================================================================
OAK_INN_GIFT:                Coord = (540, 1200)
OAK_INN_CLAIM:               Coord = (540, 1400)


# =============================================================================
# Friends list (companion send/receive)
# =============================================================================
FRIENDS_SEND_ALL:            Coord = (300, 1720)
FRIENDS_RECEIVE_ALL:         Coord = (780, 1720)
FRIENDS_CLOSE:               Coord = (940, 260)


# =============================================================================
# Guild Hall
# =============================================================================
GUILD_HALL_ENTRY:            Coord = (540, 700)
GUILD_HUNT_ICON:             Coord = (540, 700)
GUILD_BOSS_WRIZZ:            Coord = (360, 1000)
GUILD_BOSS_SOREN:            Coord = (720, 1000)
GUILD_BOSS_CHALLENGE:        Coord = (540, 1700)
GUILD_BATTLE_BEGIN:          Coord = (540, 1700)
GUILD_QUEST_TAB:             Coord = (820, 260)
GUILD_QUEST_COLLECT_ALL:     Coord = (540, 1700)


# =============================================================================
# Store (Ranhorn -> Store)
# =============================================================================
STORE_REFRESH_BUTTON:        Coord = (960, 280)

# 3x3 shop grid — row x column.
# (2 rows x 3 columns typical; some screens have 3x3).
STORE_SLOTS = [
    # (row, col): coord
    (215, 820),  (540, 820),  (865, 820),   # Row 1 (gold items: essence, POE, etc.)
    (215, 1150), (540, 1150), (865, 1150),  # Row 2
    (215, 1480), (540, 1480), (865, 1480),  # Row 3 (diamond items)
]

# Individual purchase buttons after tapping a slot.
STORE_BUY_BUTTON:            Coord = (660, 1350)
STORE_PURCHASE_CLOSE:        Coord = (540, 1700)


# =============================================================================
# Dark Forest buildings
# =============================================================================
FOREST_ARENA:                Coord = (540, 820)
FOREST_KINGS_TOWER:          Coord = (540, 540)
FOREST_LABYRINTH:            Coord = (260, 1100)
FOREST_BOUNTY_BOARD:         Coord = (820, 1100)
FOREST_LEGENDS_CHALLENGER:   Coord = (800, 820)
FOREST_TEMPORAL_RIFT:        Coord = (260, 820)


# =============================================================================
# King's Tower (and Faction Towers)
# =============================================================================
KT_ENTER:                    Coord = (540, 1100)
KT_CHALLENGE:                Coord = (540, 1700)
KT_BATTLE_BEGIN:             Coord = (540, 1700)
KT_CONTINUE_AFTER_WIN:       Coord = (540, 1700)

# Faction tower selection (4 towers on the KT hub screen).
KT_TOWER_LIGHTBEARER:        Coord = (300, 750)
KT_TOWER_MAULER:             Coord = (780, 750)
KT_TOWER_WILDER:             Coord = (300, 1150)
KT_TOWER_GRAVEBORN:          Coord = (780, 1150)


# =============================================================================
# Arena of Heroes + Legends' Challenger
# =============================================================================
ARENA_AOH_BATTLE:            Coord = (540, 1700)  # "Battle" button
# 5 opponent slots, ranked 1-5 top-down (slot 5 = weakest).
ARENA_OPPONENT_SLOTS = [
    (860, 730),   # Slot 1 (highest rank)
    (860, 900),
    (860, 1070),
    (860, 1240),
    (860, 1410),  # Slot 5 (lowest rank — pick this)
]
ARENA_PICK_WEAKEST:          Coord = (860, 1410)
ARENA_BATTLE_BEGIN:          Coord = (540, 1700)
ARENA_COLLECT_REWARDS:       Coord = (540, 1700)

# Legends' Challenger Tournament (separate from Arena of Heroes).
CHALLENGER_ENTER:            Coord = (540, 1100)
CHALLENGER_BATTLE:           Coord = (540, 1400)


# =============================================================================
# Bounty Board
# =============================================================================
BOUNTY_COLLECT_ALL:          Coord = (300, 1800)
BOUNTY_AUTO_DISPATCH:        Coord = (780, 1800)
BOUNTY_DISPATCH_CONFIRM:     Coord = (660, 1200)


# =============================================================================
# Heroes screen (for leveling + gear)
# =============================================================================
HEROES_FIRST_PORTRAIT:       Coord = (170, 470)
HEROES_GRID = [              # 4-column grid of hero portraits, first 8 rows
    (170, 470),  (430, 470),  (660, 470),  (910, 470),
    (170, 700),  (430, 700),  (660, 700),  (910, 700),
]
HERO_LEVEL_UP_BUTTON:        Coord = (540, 1700)
HERO_ENHANCE_GEAR:           Coord = (260, 1700)


# =============================================================================
# Redemption codes
# =============================================================================
MORE_MENU_SETTINGS:          Coord = (870, 260)   # In the "More"/Chat tab
SETTINGS_REDEEM_CODE:        Coord = (540, 900)
CODE_INPUT_FIELD:            Coord = (540, 800)
CODE_REDEEM_BUTTON:          Coord = (540, 1050)


# =============================================================================
# Battle result screen buttons
# =============================================================================
BATTLE_CONTINUE:             Coord = (540, 1700)  # Post-victory continue
BATTLE_RETRY:                Coord = (540, 1700)  # Post-defeat retry
BATTLE_CLOSE:                Coord = (960, 260)


# =============================================================================
# Labyrinth / Dismal Maze
# =============================================================================
LAB_ENTER:                   Coord = (540, 1100)
LAB_DISMAL_MAZE:             Coord = (350, 1000)
LAB_BEGIN:                   Coord = (540, 1700)
LAB_MOVE_UP:                 Coord = (540, 900)   # Tap-to-walk center-up


# =============================================================================
# Pixel color verification points
# =============================================================================
# (x, y, expected_rgb) — used by Vision.pixel_matches for lightweight
# "are we on the expected screen" checks. Tolerance is built into pixel_matches.
VERIFY_CAMPAIGN_NAV_ACTIVE = (540, 1870, (255, 255, 255))  # Campaign tab highlighted
VERIFY_DARK_FOREST_HEADER  = (540, 140, (100, 150, 100))   # Green forest header
VERIFY_RANHORN_HEADER      = (540, 140, (220, 190, 130))   # Warm Ranhorn palette
