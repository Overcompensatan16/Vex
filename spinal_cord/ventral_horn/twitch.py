"""Twitch kernel utilities used by :mod:`spinal_cord.ventral_horn`."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List


def twitch_kernel(elapsed_ms: float, amplitude: float, tau_rise: float) -> float:
    """Return the instantaneous twitch response for ``elapsed_ms``.

    The kernel is intentionally inexpensive and smooth which keeps unit tests
    deterministic.  Values for ``tau_rise`` roughly follow twitch rise times for
    slow (≈30 ms) and fast (≈15 ms) motor units.
    """

    if elapsed_ms < 0.0 or tau_rise <= 0.0:
        return 0.0
    scaled = elapsed_ms / tau_rise
    return amplitude * scaled * math.exp(1.0 - scaled)


@dataclass
class TwitchIntegrator:
    """Accumulates twitch events and produces a low-pass activation signal."""

    window_ms: float = 300.0
    activation_tau: float = 90.0
    activation_gain: float = 0.018
    activation: float = 0.0
    last_time: float = 0.0
    _pending_events: List[Dict[str, float]] = field(default_factory=list)
    _history: List[Dict[str, float]] = field(default_factory=list)

    def reset(self, time: float = 0.0) -> None:
        self.activation = 0.0
        self.last_time = time
        self._pending_events.clear()
        self._history.clear()

    def step_to(self, time: float) -> None:
        if time <= self.last_time:
            return
        dt = time - self.last_time
        if self.activation_tau > 0:
            self.activation *= math.exp(-dt / self.activation_tau)
        else:
            self.activation = 0.0
        self.activation = max(0.0, min(1.0, self.activation))
        self.last_time = time
        self._prune_history()

    def add_spike(self, time: float, mn_id: int, amplitude: float, tau_c: float, activation_scale: float | None = None) -> None:
        self.step_to(time)
        event = {"mn_id": mn_id, "amp": amplitude, "tau_c": tau_c, "t": time}
        self._pending_events.append(event)
        self._history.append(event)
        gain = activation_scale if activation_scale is not None else self.activation_gain
        self.activation = max(0.0, min(1.0, self.activation + gain * amplitude))
        self._prune_history()

    def _prune_history(self) -> None:
        cutoff = self.last_time - self.window_ms
        if cutoff <= 0:
            return
        self._history = [ev for ev in self._history if ev["t"] >= cutoff]

    def instantaneous_force(self, time: float) -> float:
        self.step_to(time)
        total = 0.0
        for event in self._history:
            total += twitch_kernel(time - event["t"], event["amp"], event["tau_c"])
        return total

    def collect_events(self) -> List[Dict[str, float]]:
        events = list(self._pending_events)
        self._pending_events.clear()
        return events
