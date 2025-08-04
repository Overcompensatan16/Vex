"""Synthetic limbic system core.

This module implements a simplified version of the design outlined in
``README.md``.  It integrates with the :mod:`thalamus` for salience scoring and
uses the temporal lobe ``ContextTracker`` to keep short term history of moral
evaluations.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Optional, Callable, Tuple

from cerebral_cortex.temporal_lobe.context_tracker import ContextTracker
from limbic_system.limbic_trees import QliphothTree, SephirotTree
from limbic_system.emotion import EmotionState
from limbic_system.limbic_utils import (
    compute_salience,
    compute_salience_score,
    build_moral_path,
    blend_score,
    check_balance,
)

try:  # Optional import so the limbic system can run stand-alone in tests
    from thalamus.thalamus_module import ThalamusModule
except Exception:  # pragma: no cover - import guard
    ThalamusModule = Any  # type: ignore

try:
    from fact_router import route_and_write_fact
except Exception:  # pragma: no cover - optional␊
    route_and_write_fact = None  # type: ignore


class LimbicSystem:
    """Evaluate signals for moral and emotional context."""

    def __init__(
        self,
        config_path: str = "limbic_system/limbic_config.json",
        *,
        thalamus: Optional[ThalamusModule] = None,
        context_size: int = 10,
        memory_router: Optional[Callable[[dict], Tuple[bool, str]]] = None,
        store_history: bool = True,
    ) -> None:
        self.sephirot = SephirotTree()
        self.qliphoth = QliphothTree()
        self.thalamus = thalamus
        self.context = ContextTracker(max_size=context_size, name="limbic_context")
        self.memory_router = memory_router or route_and_write_fact
        self.store_history = store_history

        cfg = self._load_config(config_path)
        self.allowance_slider = cfg.get("allowance_slider", "basic")

        # Weight values for symbolic nodes
        self.weights = {
            "Keter": 0.9,
            "Chokmah": 0.8,
            "Binah": 0.8,
            "Chesed": 0.7,
            "Gevurah": 0.7,
            "Tiphareth": 0.6,
            "Netzach": 0.5,
            "Hod": 0.5,
            "Yesod": 0.4,
            "Malkuth": 0.3,
            "Thaumiel": -0.9,
            "Chagidiel": -0.8,
            "Belial": -0.8,
            "Sathariel": -0.8,
            "Gamaliel": -0.7,
            "Golachab": -0.7,
            "Togarini": -0.6,
            "Harab Serapel": -0.6,
            "Samael": -0.5,
            "Naamah": -0.4,
            "Lilith": -0.3,
        }

    @staticmethod
    def _load_config(path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return {}

    def evaluate_signal(self, signal: Any) -> dict:
        if self.thalamus and hasattr(self.thalamus, "score_signal"):
            signal = self.thalamus.score_signal(signal)

        obj = signal.as_dict() if hasattr(signal, "as_dict") else dict(signal)

        salience_tags = compute_salience(obj)
        salience_scores = compute_salience_score(obj)
        moral, shadow = build_moral_path(obj, self.sephirot, self.qliphoth)
        moral_gravity = {tag: self.weights.get(tag, 0.0) for tag in moral + shadow}

        emotion_state = EmotionState(
            primary=salience_tags[0] if salience_tags else "neutral",
            intensity=max(salience_scores.values()) if salience_scores else 0.0,
            blends=[(t, s) for t, s in salience_scores.items()],
        )
        emotional_valence = {
            node: blend_score(emotion_state, self.sephirot.affinity.get(node, {}).get("emotion_affinity", []))
            if node in self.sephirot.nodes
            else blend_score(emotion_state, self.qliphoth.affinity.get(node, {}).get("emotion_affinity", []))
            for node in moral + shadow
        }
        moral_tension = check_balance(moral, shadow)

        fusion_nodes = []
        if "Chesed" in moral and "Gevurah" in moral:
            fusion_nodes.append("Chesed + Gevurah")
        pain_score = 0.3 if fusion_nodes else 0.0

        pain_level = "bruise" if "pain" in obj.get("tags", []) else "scratch"

        result = self._format_output(
            salience_tags,
            salience_scores,
            moral,
            shadow,
            pain_level,
            moral_gravity,
            emotional_valence,
            moral_tension,
            fusion_nodes,
            pain_score,
        )
        self.context.add({"input": obj, "result": result})
        if self.store_history and self.memory_router:
            self._route_to_memory(obj, result)
        return result

    def _format_output(
        self,
        salience_tags: list[str],
        salience_scores: dict[str, float],
        moral_path: list[str],
        shadow_path: list[str],
        pain: str,
        moral_gravity: dict[str, float],
        emotional_valence: dict[str, float],
        moral_tension: float,
        fusion_nodes: list[str],
        pain_score: float,
    ) -> dict:
        depth = (self.allowance_slider or "basic").lower()

        if depth == "basic":
            return {
                "emotional_state": " + ".join(salience_tags) if salience_tags else "neutral",
                "reasoning_depth": "basic",
            }
        if depth == "intermediate":
            return {
                "emotional_state": " + ".join(salience_tags) if salience_tags else "neutral",
                "moral_summary": " -> ".join(moral_path) if moral_path else "",
                "pain_level": pain,
                "moral_tension": moral_tension,
                "fusion_nodes": fusion_nodes,
                "pain_score": pain_score,
                "reasoning_depth": "intermediate",
            }

        return {
            "emotional_salience": salience_scores,
            "moral_path": moral_path,
            "shadow_path": shadow_path,
            "moral_gravity": moral_gravity,
            "pain_level": pain,
            "emotional_valence": emotional_valence,
            "moral_tension": moral_tension,
            "fusion_nodes": fusion_nodes,
            "pain_score": pain_score,
            "reasoning_depth": "advanced",
        }

    def _route_to_memory(self, signal: dict, evaluation: dict) -> None:
        if not self.memory_router:
            return
        record = {
            "fact": f"Limbic evaluation of {signal.get('data', '')}",
            "type": "emotion",
            "source": signal.get("source", "limbic_system"),
            "tags": signal.get("tags", []) + ["limbic"],
            "evaluation": evaluation,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        try:
            stored, path = self.memory_router(record)
            if not path:
                return
        except Exception:
            pass

    def set_allowance_slider(self, level: str) -> None:
        self.allowance_slider = level


__all__ = ["LimbicSystem"]
