"""Phase detection — early / mid / late game progression logic."""

from __future__ import annotations

from enum import Enum


class Phase(str, Enum):
    EARLY = "phase_1"  # Chapters 1-15
    MID   = "phase_2"  # Chapters 16-25
    LATE  = "phase_3"  # Chapters 26+ (RC Cramming)


def detect_phase(chapter: int) -> Phase:
    if chapter <= 15:
        return Phase.EARLY
    if chapter <= 25:
        return Phase.MID
    return Phase.LATE


def should_summon(phase: Phase) -> bool:
    """Phase 1-2: summon aggressively. Phase 3: stop summoning, spend on leveling."""
    return phase in (Phase.EARLY, Phase.MID)


def should_rc_cram(phase: Phase) -> bool:
    return phase is Phase.LATE
