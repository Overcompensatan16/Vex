"""Lightweight symbolic DesireEngine using a simple DBN stub."""
from __future__ import annotations

import json
import math
import os
import random
from dataclasses import dataclass
from typing import List

from symbolic_signal import DesireSignal


@dataclass
class DesireModulator:
    """Container for modulatory inputs to the DesireEngine."""

    pineal: List[float]
    personality: List[float]
    context: List[float]

    def as_vector(self) -> List[float]:
        return self.pineal + self.personality + self.context


class _RBMLayer:
    """Very small RBM layer used for the DBN."""

    def __init__(self, visible: int, hidden: int) -> None:
        self.visible = visible
        self.hidden = hidden
        self.weights = [
            [random.uniform(-0.1, 0.1) for _ in range(hidden)] for _ in range(visible)
        ]
        self.h_bias = [0.0 for _ in range(hidden)]

    def forward(self, v: List[float]) -> List[float]:
        result = []
        for j in range(self.hidden):
            s = self.h_bias[j]
            for i in range(self.visible):
                s += v[i] * self.weights[i][j]
            result.append(1 / (1 + math.exp(-s)))
        return result


class _DBN:
    def __init__(self, sizes: List[int]) -> None:
        self.layers = [
            _RBMLayer(sizes[i], sizes[i + 1]) for i in range(len(sizes) - 1)
        ]

    def forward(self, v: List[float]) -> List[float]:
        for layer in self.layers:
            v = layer.forward(v)
        return v


class DesireFilter:
    """Simple gating logic for generated desires."""

    confidence_threshold: float = 0.65

    @classmethod
    def apply(cls, signal: DesireSignal) -> DesireSignal | None:
        if signal.confidence < cls.confidence_threshold:
            return None
        return signal


class DesireEngine:
    """Generate symbolic desires from DBN activations."""

    MODULES = ["VexMusicPlugin", "FileScanner", "IdleActivity"]
    TYPES = ["creative", "exploratory", "stabilizing"]

    _dbn = _DBN([7, 5, 3])  # simple 2-layer DBN: input->hidden->output
    _log_path = os.path.join("AI_Audit", "limbic_system", "desire_log.jsonl")

    @classmethod
    def generate_desire(cls, mod: DesireModulator) -> DesireSignal | None:
        vector = mod.as_vector()
        out = cls._dbn.forward(vector)
        mod_idx = int(out[0] * len(cls.MODULES)) % len(cls.MODULES)
        conf = max(0.0, min(1.0, out[1]))
        type_idx = int(out[2] * len(cls.TYPES)) % len(cls.TYPES)
        signal = DesireSignal(
            module=cls.MODULES[mod_idx],
            confidence=conf,
            type=cls.TYPES[type_idx],
        )
        filtered = DesireFilter.apply(signal)
        cls._log(vector, signal)
        return filtered

    @classmethod
    def _log(cls, vector: List[float], signal: DesireSignal) -> None:
        entry = {
            "input_vector": vector,
            "desire": signal.as_dict(),
        }
        try:
            with open(cls._log_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")
        except Exception:
            pass


__all__ = ["DesireEngine", "DesireModulator", "DesireFilter"]
