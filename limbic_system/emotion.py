from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple, Dict


# ----------------------------- Plutchik to VAD mapping -----------------------------
PLUTCHIK_TO_VAD: Dict[str, Tuple[float, float, float]] = {
    "joy":          (0.9, 0.7, 0.6),
    "trust":        (0.7, 0.4, 0.5),
    "fear":         (-0.8, 0.8, 0.2),
    "surprise":     (0.1, 0.9, 0.3),
    "sadness":      (-0.9, 0.5, 0.1),
    "disgust":      (-0.7, 0.6, 0.2),
    "anger":        (-0.6, 0.8, 0.7),
    "anticipation": (0.3, 0.6, 0.5),
}


# ----------------------------- EmotionState class -----------------------------
@dataclass
class EmotionState:
    """Represents a Plutchik-derived emotional state with VAD metrics."""

    primary: str
    intensity: float
    blends: List[Tuple[str, float]] = field(default_factory=list)

    # Valence (-1.0 negative → +1.0 positive), arousal (0→1), dominance (0→1)
    valence: float = 0.0
    arousal: float = 0.0
    dominance: float = 0.0

    timestamp: datetime = field(default_factory=datetime.utcnow)
    decay_rate: float = 0.05  # per tick decay of intensity

    def __post_init__(self):
        # Initialize VAD from mapping if primary matches
        if self.primary in PLUTCHIK_TO_VAD and self.valence == 0 and self.arousal == 0 and self.dominance == 0:
            v, a, d = PLUTCHIK_TO_VAD[self.primary]
            self.valence, self.arousal, self.dominance = v, a, d

    # ----------------------------- Serialization -----------------------------
    def as_dict(self) -> Dict:
        return {
            "primary": self.primary,
            "intensity": self.intensity,
            "blends": self.blends,
            "valence": self.valence,
            "arousal": self.arousal,
            "dominance": self.dominance,
            "timestamp": self.timestamp.isoformat(),
        }

    # ----------------------------- Update & Decay -----------------------------
    def update_intensity(self, delta: float):
        """Adjust intensity with clamping."""
        self.intensity = max(0.0, min(1.0, self.intensity + delta))

    def decay(self):
        """Decay emotion intensity over time."""
        self.intensity = max(0.0, self.intensity * (1 - self.decay_rate))

    # ----------------------------- Blending -----------------------------
    def blend_with(self, other: EmotionState) -> EmotionState:
        """Return a new emotion state blended from self and other."""
        w1, w2 = self.intensity, other.intensity
        total = w1 + w2
        if total == 0:
            return self

        valence = (self.valence * w1 + other.valence * w2) / total
        arousal = (self.arousal * w1 + other.arousal * w2) / total
        dominance = (self.dominance * w1 + other.dominance * w2) / total
        blends = self.blends + [(other.primary, other.intensity)]

        return EmotionState(
            primary=self.primary if w1 >= w2 else other.primary,
            intensity=min(1.0, total),
            blends=blends,
            valence=valence,
            arousal=arousal,
            dominance=dominance,
        )

    # ----------------------------- Categories for reasoning -----------------------------
    def category(self) -> str:
        """Return a symbolic emotion category for reasoning modules."""
        if self.valence > 0.5 and self.arousal > 0.5:
            return "excited_positive"
        if self.valence < -0.5 and self.arousal > 0.5:
            return "high_arousal_negative"
        if self.valence < -0.5 and self.arousal < 0.5:
            return "calm_negative"
        return "neutral_or_mixed"


# ----------------------------- Utilities -----------------------------
def average_emotions(emotions: List[EmotionState]) -> EmotionState | None:
    """Compute the weighted average of multiple emotion states."""
    if not emotions:
        return None

    total_intensity = sum(e.intensity for e in emotions)
    if total_intensity == 0:
        return emotions[0]

    valence = sum(e.valence * e.intensity for e in emotions) / total_intensity
    arousal = sum(e.arousal * e.intensity for e in emotions) / total_intensity
    dominance = sum(e.dominance * e.intensity for e in emotions) / total_intensity

    # Choose primary by highest intensity
    primary = max(emotions, key=lambda e: e.intensity).primary
    blends = [(e.primary, e.intensity) for e in emotions if e.primary != primary]

    return EmotionState(
        primary=primary,
        intensity=min(1.0, total_intensity / len(emotions)),
        blends=blends,
        valence=valence,
        arousal=arousal,
        dominance=dominance,
    )


__all__ = [
    "EmotionState",
    "average_emotions",
    "PLUTCHIK_TO_VAD",
]

