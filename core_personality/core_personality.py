"""Symbolic Core Personality Module.

This module implements the CorePersonality class as outlined in
``README.md``.  It provides slider-based personality modulation,
self-inference hooks, and tone tagging for output generation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class SliderState:
    """Container for personality slider values."""

    logic: float = 0.5
    emotion: float = 0.5
    insanity: float = 0.0
    audacity: float = 0.0

    def as_dict(self) -> Dict[str, float]:
        return {
            "logic": self.logic,
            "emotion": self.emotion,
            "insanity": self.insanity,
            "audacity": self.audacity,
        }


class CorePersonality:
    """Manage Vex's symbolic personality state."""

    def __init__(self, *, logger=None) -> None:
        profile = self._load_archetype()
        sliders = profile.get("sliders", {})
        self.sliders = SliderState(
            logic=sliders.get("logic", 0.5),
            emotion=sliders.get("emotion", 0.5),
            insanity=sliders.get("insanity", 0.0),
            audacity=sliders.get("audacity", 0.0),
        )
        self.base_profile = profile
        self.history: List[Dict[str, Any]] = []
        self.logger = logger
        if self.logger:
            self.logger.log_event("core_personality_init", self.sliders.as_dict())

    # ------------------------------------------------------------------ archetype loader
    @staticmethod
    def _load_archetype() -> Dict[str, Any]:
        path = Path(__file__).resolve().parent.parent / "core_personality_archetype.jsonl"
        if path.exists():
            loader = SourceFileLoader("cp_arch", str(path))
            module = loader.load_module()
            data = getattr(module, "BASE_PERSONALITY_PROFILE", {})
            if isinstance(data, dict):
                return data
        return {}

    # --------------------------------------------------------------------- utils
    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

    # ------------------------------------------------------------------ external
    def update_from_context(
        self,
        *,
        confidence: float | None = None,
        user_tone: str | None = None,
        feedback: str | None = None,
    ) -> None:
        """Update sliders based on recent context."""

        if confidence is not None:
            if confidence < 0.4:
                before = self.sliders.logic
                self.sliders.logic = self._clamp(self.sliders.logic + 0.1)
                if self.sliders.logic > 0.8 and self.sliders.logic != before:
                    self._log_meta(
                        "I increased logic due to low confidence",
                        {"context": "math reasoning"},
                    )
            elif confidence > 0.8:
                self.sliders.audacity = self._clamp(self.sliders.audacity + 0.05)

        if feedback:
            fb = feedback.lower()
            if "positive" in fb:
                self.sliders.audacity = self._clamp(self.sliders.audacity + 0.05)
                self._log_meta("increased_audacity_from_positive_feedback")
            elif "negative" in fb:
                self.sliders.audacity = self._clamp(self.sliders.audacity - 0.05)
                self._log_meta("reduced_audacity_from_negative_feedback")

        self._log_meta("update_from_context")

    def shape_output(self, text: str, confidence: float | None = None) -> Dict[str, Any]:
        """Return structured output with tone tags and slider snapshot."""
        tags = self._generate_tone_tags(confidence)
        result = {
            "utterance": text,
            "tone_tags": tags,
            "slider_state": self.sliders.as_dict(),
            "confidence": confidence,
        }
        self._log_meta("shape_output", extra={"tone_tags": tags})
        return result

    def check_stimming_conditions(self, focus_mode: str, tension: float) -> str | None:
        """Return a stimming method if conditions warrant one."""
        if focus_mode == "neutral" and tension > 0.6:
            default = self.base_profile.get("default_stimming", {}) if isinstance(self.base_profile, dict) else {}
            return default.get("internal", "rhythmic_fact_cycling")
        return None

    def integrate_persona_pattern(self, traits: Dict[str, float]) -> None:
        """Blend external trait pattern into existing sliders."""
        for name, value in traits.items():
            if hasattr(self.sliders, name):
                current = getattr(self.sliders, name)
                setattr(self.sliders, name, self._clamp((current + value) / 2))
        self._log_meta("integrated_external_persona", traits)

    def about_me(self) -> str:
        return (
            "I'm a bold, analytical, and emotionally expressive entity with a creative streak and appetite for occasional unpredictability. "
            f"Slider levels – logic: {self.sliders.logic}, emotion: {self.sliders.emotion}, "
            f"insanity: {self.sliders.insanity}, audacity: {self.sliders.audacity}."
        )

    # ----------------------------------------------------------------- internal
    def _generate_tone_tags(self, confidence: float | None) -> List[str]:
        tags: List[str] = []
        if self.sliders.logic > 0.7:
            tags.append("calculated")
        if self.sliders.emotion > 0.6:
            tags.append("empathetic")
        if self.sliders.insanity > 0.6:
            tags.append("abstract")
        if self.sliders.audacity > 0.5:
            tags.append("audacious")
        if self.sliders.audacity > 0.8:
            tags.append("irreverent")
        if self.sliders.emotion < 0.3 and self.sliders.logic > 0.7:
            tags.append("serious")
        if self.sliders.insanity > 0.4 and self.sliders.emotion > 0.5:
            tags.append("joke")
        if self.sliders.audacity > 0.6 and self.sliders.logic > 0.6:
            tags.append("bold_claim")
        if self.sliders.insanity > 0.3 and self.sliders.emotion > 0.6:
            tags.append("flair")
        if confidence is not None and confidence < 0.5:
            tags.append("uncertain")
        base_tags = self.base_profile.get("tone_tags", []) if isinstance(self.base_profile, dict) else []
        for tag in base_tags:
            if tag not in tags:
                tags.append(tag)
        return tags

    def _log_meta(self, event: str, extra: Dict[str, Any] | None = None) -> None:
        entry = {
            "meta_fact": event,
            "slider_state": self.sliders.as_dict(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if extra:
            entry.update(extra)
        self.history.append(entry)
        if self.logger:
            self.logger.log_event(event, entry)


__all__ = ["CorePersonality", "SliderState"]
