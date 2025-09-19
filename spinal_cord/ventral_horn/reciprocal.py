"""Reciprocal inhibition interneuron model."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class ReciprocalInterneuron:
    """Smooth inhibition level based on antagonist activity."""

    tau: float = 12.0
    gain: float = 1.3
    level: float = 0.0
    last_update: float = 0.0

    def reset(self, time: float = 0.0) -> None:
        self.level = 0.0
        self.last_update = time

    def receive_antagonist_spike(self, time: float, weight: float = 1.0) -> None:
        self.step_until(time)
        self.level += weight

    def step_until(self, target_time: float) -> None:
        if target_time <= self.last_update:
            return
        dt = target_time - self.last_update
        if self.tau > 0:
            self.level *= math.exp(-dt / self.tau)
        self.last_update = target_time

    @property
    def inhibitory_level(self) -> float:
        return self.level * self.gain
