"""Formation selection helpers — pick the best formation for current progress."""

from __future__ import annotations

from typing import Dict, List, Optional

from .meta import FORMATIONS


def formation_for_chapter(chapter: int) -> List[str]:
    """Return an ordered list of formation names to try for a given chapter."""
    if chapter <= 20:
        return ["early_daimon", "early_daimon_alt"]
    if chapter <= 30:
        return ["five_pull", "ainz_comp", "early_daimon_alt"]
    if chapter <= 35:
        return ["five_pull", "alna_grezhul", "ainz_comp"]
    return ["alna_grezhul", "thoran_cheese", "liberta_charm", "five_pull"]


def get_formation(name: str) -> Optional[Dict]:
    return FORMATIONS.get(name)
