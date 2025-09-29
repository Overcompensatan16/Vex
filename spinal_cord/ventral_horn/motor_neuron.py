"""Conductance based leaky integrate-and-fire motor neuron models."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List


@dataclass
class MotorNeuron:
    """Simple gLIF motor neuron with exponential synapses.

    The implementation purposefully favours clarity over micro-optimisation.  We
    step individual neurons only when a pool requests it, which keeps the system
    effectively event driven while still providing deterministic integration for
    unit tests.  All units share a common integration step ``dt`` expressed in
    milliseconds.
    """

    mn_id: int
    size_index: int
    C_m: float
    g_L: float
    E_L: float
    V_th: float
    V_reset: float
    dt: float
    tau_exc: float = 6.0
    tau_inh: float = 12.0
    E_exc: float = 0.0
    E_inh: float = -70.0
    threshold_offset: float = 0.0
    bias_current: float = 0.0
    refractory_period: float = 4.5

    V: float = field(init=False)
    g_exc: float = field(default=0.0, init=False)
    g_inh: float = field(default=0.0, init=False)
    last_update: float = field(default=0.0, init=False)
    spike_times: List[float] = field(default_factory=list, init=False)
    _recent_spike_flag: bool = field(default=False, init=False)
    _last_drive: float = field(default=0.0, init=False)
    _refractory_until: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:  # pragma: no cover - trivial
        self.V = self.E_L

    @property
    def dynamic_threshold(self) -> float:
        return self.V_th + self.threshold_offset

    def reset(self, time: float = 0.0) -> None:
        self.V = self.E_L
        self.g_exc = 0.0
        self.g_inh = 0.0
        self.last_update = time
        self.spike_times.clear()
        self._recent_spike_flag = False
        self._last_drive = 0.0
        self._refractory_until = time

    def set_threshold_offset(self, offset: float) -> None:
        self.threshold_offset = offset

    def set_bias_current(self, value: float) -> None:
        self.bias_current = value

    def _apply_decay(self, step: float) -> None:
        if self.tau_exc > 0:
            self.g_exc *= math.exp(-step / self.tau_exc)
        if self.tau_inh > 0:
            self.g_inh *= math.exp(-step / self.tau_inh)

    def _integrate_step(self, step: float, current_time: float, spikes: List[float]) -> None:
        self._apply_decay(step)

        if current_time < self._refractory_until:
            self.V = self.V_reset
            self._last_drive = 0.0
            return

        I_exc = self.g_exc * (self.E_exc - self.V)
        I_inh = self.g_inh * (self.E_inh - self.V)
        I_syn = I_exc + I_inh + self.bias_current
        dV = (-self.g_L * (self.V - self.E_L) + I_syn) * (step / self.C_m)
        self.V += dV
        self._last_drive = I_exc - abs(I_inh)

        if self.V >= self.dynamic_threshold:
            self.V = self.V_reset
            self._refractory_until = current_time + self.refractory_period
            spikes.append(current_time)
            self.spike_times.append(current_time)
            self._recent_spike_flag = True

    def step_until(self, target_time: float) -> List[float]:
        if target_time <= self.last_update:
            return []

        spikes: List[float] = []
        current = self.last_update
        self._recent_spike_flag = False

        while current + self.dt <= target_time:
            current += self.dt
            self._integrate_step(self.dt, current, spikes)

        remainder = target_time - current
        if remainder > 1e-9:
            current = target_time
            self._integrate_step(remainder, current, spikes)

        self.last_update = target_time
        return spikes

    def receive_excitation(self, time: float, weight: float) -> None:
        if time > self.last_update:
            self.step_until(time)
        self.g_exc += weight

    def receive_inhibition(self, time: float, weight: float) -> None:
        if time > self.last_update:
            self.step_until(time)
        self.g_inh += weight

    def firing_rate(self, current_time: float, window_ms: float = 100.0) -> float:
        if not self.spike_times:
            return 0.0
        lower_bound = current_time - window_ms
        count = 0
        for spike in reversed(self.spike_times):
            if spike < lower_bound:
                break
            count += 1
        if window_ms <= 0:
            return 0.0
        return (count / (window_ms / 1000.0)) if count else 0.0

    @property
    def recent_spike(self) -> bool:
        return self._recent_spike_flag

    @property
    def last_drive(self) -> float:
        return self._last_drive
