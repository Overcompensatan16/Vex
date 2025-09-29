"""Simplified Renshaw cell dynamics."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List


@dataclass
class RenshawCell:
    """Low order Renshaw loop model.

    The cell behaves as a leaky integrator that receives collateral spikes from
    α-motor neurons.  Its activity is converted into glycinergic inhibition that
    feeds back onto the same motor pool and mildly onto γ neurons.  The model is
    intentionally compact yet captures the stabilising influence of the Renshaw
    circuit.
    """

    tau_ampa: float = 6.0
    tau_output: float = 15.0
    collateral_gain: float = 0.75
    glycine_gain: float = 1.05

    g_ampa: float = 0.0
    level: float = 0.0
    last_update: float = 0.0
    activity_trace: List[float] = None

    def __post_init__(self) -> None:  # pragma: no cover - trivial
        if self.activity_trace is None:
            self.activity_trace = []

    def reset(self, time: float = 0.0) -> None:
        self.g_ampa = 0.0
        self.level = 0.0
        self.last_update = time
        self.activity_trace.clear()

    def receive_spike(self, time: float, weight: float = 1.0) -> None:
        self.step_until(time)
        self.g_ampa += weight * self.collateral_gain

    def step_until(self, target_time: float) -> None:
        if target_time <= self.last_update:
            return
        dt = target_time - self.last_update
        if self.tau_ampa > 0:
            self.g_ampa *= math.exp(-dt / self.tau_ampa)
        if self.tau_output > 0:
            self.level *= math.exp(-dt / self.tau_output)
        self.level += self.g_ampa * (1.0 - math.exp(-dt / self.tau_output))
        self.last_update = target_time
        self.activity_trace.append(self.level)
        if len(self.activity_trace) > 64:
            self.activity_trace.pop(0)

    @property
    def glycinergic_level(self) -> float:
        return self.level * self.glycine_gain
