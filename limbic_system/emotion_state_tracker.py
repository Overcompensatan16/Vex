from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timedelta

from emotions import EmotionState, average_emotions  # uses the upgraded emotions.py

class EmotionManager:
    """Tracks current emotions, applies decay, and provides tags for reasoning modules."""

    def __init__(self, decay_interval: float = 5.0):
        """
        Args:
            decay_interval: Seconds between automatic decay steps.
        """
        self.active: List[EmotionState] = []
        self.last_decay = datetime.utcnow()
        self.decay_interval = timedelta(seconds=decay_interval)

    # ---------------------- Emotion Updates ----------------------
    def add_emotion(self, emotion: EmotionState) -> None:
        """Add or blend a new emotion into the active list."""
        # If the same primary exists, blend them
        for i, e in enumerate(self.active):
            if e.primary == emotion.primary:
                self.active[i] = e.blend_with(emotion)
                return
        self.active.append(emotion)

    def decay_emotions(self) -> None:
        """Decay all emotions based on decay_rate."""
        now = datetime.utcnow()
        if now - self.last_decay >= self.decay_interval:
            for e in self.active:
                e.decay()
            # Remove emotions that fully decayed
            self.active = [e for e in self.active if e.intensity > 0.01]
            self.last_decay = now

    # ---------------------- Queries ----------------------
    def dominant_emotion(self) -> Optional[EmotionState]:
        """Return the highest-intensity emotion or None if empty."""
        self.decay_emotions()
        if not self.active:
            return None
        return max(self.active, key=lambda e: e.intensity)

    def average_state(self) -> Optional[EmotionState]:
        """Return a weighted average of all active emotions."""
        self.decay_emotions()
        return average_emotions(self.active)

    def get_emotional_tag(self) -> str:
        """
        Return a symbolic tag for the current emotional state.
        Used by NGL or personality/tone systems.
        """
        self.decay_emotions()
        dom = self.dominant_emotion()
        if not dom:
            return "neutral"
        return dom.category()

    def as_dict(self) -> dict:
        """Return all active emotions as serializable dicts."""
        self.decay_emotions()
        return [e.as_dict() for e in self.active]
