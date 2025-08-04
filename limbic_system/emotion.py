from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class EmotionState:
    """Represents a Plutchik-derived emotional state."""

    primary: str
    intensity: float
    blends: List[Tuple[str, float]] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "primary": self.primary,
            "intensity": self.intensity,
            "blends": self.blends,
        }


__all__ = ["EmotionState"]
