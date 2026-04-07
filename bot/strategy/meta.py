"""AFK Arena F2P meta — April 2026 patch.

All hero tier lists, wishlist configurations, SI/Furniture priorities, and
pre-built formations live here as plain Python constants so they can be
updated easily without touching task logic.
"""

from __future__ import annotations

from typing import Dict, List


# ---------------------------------------------------------------- rerolling
REROLL_TARGET: str = "Daimon"
REROLL_ACCEPTABLE: List[str] = ["Daimon", "Rowan"]


# ----------------------------------------------------------------- wishlists
WISHLIST_EARLY: Dict[str, List[str]] = {
    "Lightbearer": ["Rowan", "Rosaline", "Scarlet", "Raine", "Estrilda"],
    "Mauler":      ["Brutus", "Skriath", "Kren", "Tidus", "Safiya"],
    "Wilder":      ["Eironn", "Lyca", "Tasi", "Raku", "Saurus"],
    "Graveborn":   ["Daimon", "Ferael", "Thoran", "Silas", "Oden"],
}

WISHLIST_MID: Dict[str, List[str]] = {
    "Lightbearer": ["Alvida", "Jerome", "Palmer", "Adrian & Elise", "Raine"],
    "Mauler":      ["Talimar", "Naroko", "Gorren", "Vika", "Villanelle"],
    "Wilder":      ["Misha", "Gorok", "Tamrus", "Atheus", "Trishea"],
    "Graveborn":   ["Randle", "Ivan", "Mira", "Bronn", "Lady Simona"],
}


# -------------------------------------------------------- carry progression
CARRY_PROGRESSION: List[Dict[str, str]] = [
    {"hero": "Wukong",  "range": "1-100",  "source": "Free from Share event"},
    {"hero": "Mirael",  "range": "100-160", "source": "Legendary fodder carry"},
    {"hero": "Daimon",  "range": "160+",    "source": "Ascended carry, SI+20"},
]

GARRISON_PRIORITY: List[Dict[str, str | int]] = [
    {"hero": "Rem",    "chapter": 7,  "notes": "Primary carry Ch7-30+"},
    {"hero": "Ainz",   "chapter": 15, "notes": "Second carry for multi-team"},
    {"hero": "Albedo", "chapter": 15, "notes": "Pairs with Ainz, SI30"},
]


# --------------------------------------------------- SI / Furniture targets
SI30_PRIORITY: List[str] = [
    "Rowan", "Albedo", "Daemia", "Alna", "Lavatune",
    "Lucretia", "Thoran", "Naroko", "Tamrus", "Jerome",
]

FURNITURE_9F: List[str] = [
    "Alna", "Awakened Shemira", "Rem", "Grezhul", "Ainz",
    "Scarlet", "Merlin", "Daemia", "Lavatune",
]

FURNITURE_3F_CRITICAL: Dict[str, str] = {
    "Skriath": "Enables 5-Pull (pulls all 5 enemies to Eironn)",
    "Zolrath": "Delays enemy entrance 0.75s",
    "Albedo":  "Immunity protects SI30 buff",
}

ENGRAVING_CAP: Dict[str, str] = {
    # NEVER engrave past these caps.
    "Thoran": "E11",
}


# ------------------------------------------------------------- formations
FORMATIONS: Dict[str, Dict] = {
    "early_daimon": {
        "front": ["Brutus", "Grezhul"],
        "back":  ["Daimon", "Rowan", "Tasi"],
        "chapters": "1-20",
    },
    "early_daimon_alt": {
        "front": ["Brutus", "Thoran"],
        "back":  ["Daimon", "Rowan", "Ferael"],
        "chapters": "1-20",
    },
    "five_pull": {
        "front": ["Skriath", "Brutus"],
        "back":  ["Eironn", "Lyca", "Tidus"],
        "chapters": "20-35",
    },
    "ainz_comp": {
        "front": ["Albedo", "Arthur"],
        "back":  ["Ainz", "Rowan", "Merlin"],
        "chapters": "20-40",
    },
    "alna_grezhul": {
        "front": ["Alna", "Grezhul"],
        "back":  ["Ferael", "Silas", "Oden"],
        "chapters": "30+",
    },
    "thoran_cheese": {
        "front": ["Thoran"],
        "back":  ["Kelthur", "Lorsan", "Pippa", "Lyca"],
        "chapters": "30+",
        "notes": "SI30 3F E11 MAX. Low gear intentionally.",
    },
    "liberta_charm": {
        "front": ["Liberta", "Brutus"],
        "back":  ["Mehira", "Rowan", "Rosaline"],
        "chapters": "35+",
    },
}


# ------------------------------------------------------------------- codes
REDEMPTION_CODES: List[str] = [
    "ujqrukd2at",
    "vdj82fht4r",
    "2bjzpbed53",
    "lilithhappy2026",
]
