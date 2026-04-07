"""Diamond spending, store buy rules, daily task order, campaign retries."""

from __future__ import annotations

from typing import Dict, List


DIAMOND_RULES: Dict[str, Dict[str, str]] = {
    "phase_1": {  # Chapters 1-15
        "summons":      "100% of diamonds -> 10x pulls (2,700 each)",
        "store":        "500 dust with gold daily, 5x soulstones for 90 diamonds",
        "fast_rewards": "Free one only",
        "chests":       "SAVE ALL — value scales with chapter",
    },
    "phase_2": {  # Chapters 16-25
        "summons":      "Primary diamond sink, continue pulling",
        "fast_rewards": "+50 diamond purchase daily from Ch16, +80 from Ch21",
        "gear_stall":   "Consider 2-3 day pause at Ch16 for Mythic gear drops",
    },
    "phase_3": {  # Chapters 26+ (RC Cramming)
        "summons":     "STOP — shift to leveling resources",
        "daily_spend": (
            "~1,000-1,500 diamonds: store refresh (200) + dust crates (300ea) "
            "+ EXP crates (192ea) + fast rewards (330) + bounty refresh"
        ),
    },
}


STORE_BUY_RULES: Dict[str, List[str]] = {
    "gold": [
        "Hero Essence (ALL)",
        "POE coins (ALL)",
    ],
    "diamonds": [
        "5x Elite Soulstones (90)",
        "Dust crates (300, Phase 3)",
        "EXP crates (192, Phase 3)",
    ],
    "never": [
        "Gold for diamonds",
        "Hero XP piles",
        "Gear",
        "Scrolls",
    ],
    "lab_store": [
        "Dimensional Stones (Rem garrison)",
        "Arthur shards",
        "Red Emblems",
    ],
    "challenger_store": [
        "Alna first",
        "Athalia second",
        "Ezizh third",
    ],
    "guild_store": [
        "Mythic gear/T1 stones ONLY",
    ],
}


DAILY_TASK_ORDER: List[str] = [
    "collect_afk_rewards",
    "claim_fast_rewards",
    "claim_daily_gift",
    "send_receive_companion",
    "collect_mail",
    "bounty_board",
    "level_hero",
    "enhance_gear",
    "guild_hunt",
    "arena_battles",
    "challenger_tournament",
    "kings_tower_attempt",
    "summon_hero",
    "collect_daily_quest_reward",
    "store_purchases",
]


CAMPAIGN_RULES: Dict[str, int | float] = {
    "max_retries": 50,
    "swap_formation_after": 20,
    "give_up_after": 100,
    "wait_hours": 4,
}


# Buttons we should NEVER tap — tokens matched by OCR or template name.
PURCHASE_TOKENS: List[str] = [
    "buy",
    "purchase",
    "spend",
    "confirm_purchase",
    "google_play",
    "paypal",
]
