"""Limbic system package."""

from limbic_system.limbic_system_module import LimbicSystem
from limbic_system.emotion import EmotionState
from limbic_system.desire_engine import DesireEngine, DesireModulator


__all__ = [
    "LimbicSystem",
    "EmotionState",
    "DesireEngine",
    "DesireModulator",
    "generate_natural_phrase",
]
