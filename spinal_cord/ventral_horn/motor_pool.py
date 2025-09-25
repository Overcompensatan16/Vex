"""Motor pool orchestration and routing."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, MutableMapping, Optional

from .motor_neuron import MotorNeuron
from .reciprocal import ReciprocalInterneuron
from .renshaw import RenshawCell
from .twitch import TwitchIntegrator


@dataclass
class MotorPoolState:
    t: float
    pool: str
    alpha_rates: List[float]
    alpha_spikes: List[bool]
    gamma_rates: List[float]
    renshaw_level: float
    reciprocal_inhibition: float
    net_drive: float


@dataclass
class MotorCommand:
    t: float
    muscle: str
    twitch_events: List[Dict[str, float]]
    activation: float
    region: str
    signals: Dict[str, float]


class MotorPool:
    """A single muscle motor pool with α, γ neurons and stabilising circuitry."""

    def __init__(
        self,
        muscle_name: str,
        region: str,
        antagonist_name: str | None = None,
        *,
        alpha_count: int = 5,
        gamma_count: int = 2,
        dt: float = 1.0,
        anesthesia_controller: Optional["AnesthesiaController"] = None,
    ) -> None:
        self.muscle_name = muscle_name
        self.region = region
        self.antagonist_name = antagonist_name
        self.pool = muscle_name.split("_")[0]
        self.pool_identifier = f"pool:{self.pool}"
        self.dt = dt
        self.anesthesia = anesthesia_controller or AnesthesiaController()

        self.alpha_mns: List[MotorNeuron] = []
        self.gamma_mns: List[MotorNeuron] = []
        self._alpha_profiles: List[Dict[str, float]] = []
        self._gamma_profiles: List[Dict[str, float]] = []

        self._build_neurons(alpha_count, gamma_count)

        self.renshaw = RenshawCell()
        self.reciprocal = ReciprocalInterneuron()
        self._antagonist: Optional[MotorPool] = None

        self._twitch = TwitchIntegrator()
        self._alpha_recent_spikes = [False] * len(self.alpha_mns)
        self._gamma_recent_spikes = [False] * len(self.gamma_mns)

        self._time = 0.0
        self._descending_bias = 0.0
        self._descending_last = 0.0
        self._descending_tau = 220.0
        self._descending_gain = 1.6

        self._net_drive = 0.0
        self._suspended_emit_logged = False

    # ------------------------------------------------------------------ factory
    def _build_neurons(self, alpha_count: int, gamma_count: int) -> None:
        alpha_defaults = [
            {"V_th": -53.0, "C_m": 0.32, "g_L": 0.012, "twitch": 0.28, "tau_c": 95.0},
            {"V_th": -52.2, "C_m": 0.34, "g_L": 0.013, "twitch": 0.4, "tau_c": 85.0},
            {"V_th": -51.2, "C_m": 0.36, "g_L": 0.014, "twitch": 0.55, "tau_c": 75.0},
            {"V_th": -50.0, "C_m": 0.39, "g_L": 0.015, "twitch": 0.72, "tau_c": 65.0},
            {"V_th": -48.8, "C_m": 0.42, "g_L": 0.016, "twitch": 0.9, "tau_c": 55.0},
        ]
        base_reset = -62.0

        for idx in range(alpha_count):
            defaults = alpha_defaults[min(idx, len(alpha_defaults) - 1)]
            neuron = MotorNeuron(
                mn_id=idx,
                size_index=idx,
                C_m=defaults["C_m"],
                g_L=defaults["g_L"],
                E_L=-65.0,
                V_th=defaults["V_th"],
                V_reset=base_reset,
                dt=self.dt,
                tau_exc=6.0,
                tau_inh=12.0,
            )
            self.alpha_mns.append(neuron)
            self._alpha_profiles.append(
                {
                    "mn_id": idx,
                    "twitch_amp": defaults["twitch"],
                    "tau_c": defaults["tau_c"],
                    "renshaw_weight": 0.8 + idx * 0.05,
                    "reciprocal_weight": 1.1 + idx * 0.15,
                    "activation_scale": 0.015 + idx * 0.002,
                }
            )

        gamma_defaults = [
            {"V_th": -50.5, "C_m": 0.28, "g_L": 0.011},
            {"V_th": -49.5, "C_m": 0.3, "g_L": 0.012},
        ]
        offset = 100
        for idx in range(gamma_count):
            defaults = gamma_defaults[min(idx, len(gamma_defaults) - 1)]
            neuron = MotorNeuron(
                mn_id=offset + idx,
                size_index=idx,
                C_m=defaults["C_m"],
                g_L=defaults["g_L"],
                E_L=-63.0,
                V_th=defaults["V_th"],
                V_reset=-60.0,
                dt=self.dt,
                tau_exc=5.5,
                tau_inh=10.0,
            )
            self.gamma_mns.append(neuron)
            self._gamma_profiles.append({"mn_id": offset + idx})

    # ----------------------------------------------------------------- lifecycle
    def reset(self, time: float = 0.0) -> None:
        for neuron in self.alpha_mns + self.gamma_mns:
            neuron.reset(time)
        self.renshaw.reset(time)
        self.reciprocal.reset(time)
        self._twitch.reset(time)
        self._time = time
        self._descending_bias = 0.0
        self._descending_last = time
        self._net_drive = 0.0
        self._alpha_recent_spikes = [False] * len(self.alpha_mns)
        self._gamma_recent_spikes = [False] * len(self.gamma_mns)
        self._suspended_emit_logged = False

    # ---------------------------------------------------------------- antagonism
    def attach_antagonist(self, pool: "MotorPool") -> None:
        self._antagonist = pool

    # ---------------------------------------------------------------- scheduling
    def _decay_descending_bias(self, target_time: float) -> None:
        if target_time <= self._descending_last:
            return
        dt = target_time - self._descending_last
        if self._descending_tau > 0:
            self._descending_bias *= math.exp(-dt / self._descending_tau)
        self._descending_last = target_time
        self._apply_threshold_offsets()

    def _apply_threshold_offsets(self) -> None:
        for idx, neuron in enumerate(self.alpha_mns):
            offset = -self._descending_bias * self._descending_gain * (1.0 - 0.15 * idx)
            neuron.set_threshold_offset(offset)
            neuron.set_bias_current(self._descending_bias * 0.02)
        for neuron in self.gamma_mns:
            neuron.set_bias_current(self._descending_bias * 0.015)

    def _advance(self, target_time: float) -> None:
        if target_time <= self._time:
            return

        self._decay_descending_bias(target_time)

        self._alpha_recent_spikes = [False] * len(self.alpha_mns)
        self._gamma_recent_spikes = [False] * len(self.gamma_mns)

        for idx, neuron in enumerate(self.alpha_mns):
            spikes = neuron.step_until(target_time)
            if spikes:
                profile = self._alpha_profiles[idx]
                for spike_time in spikes:
                    self._record_alpha_spike(profile, spike_time)
        for idx, neuron in enumerate(self.gamma_mns):
            spikes = neuron.step_until(target_time)
            self._gamma_recent_spikes[idx] = bool(spikes)

        self.renshaw.step_until(target_time)
        renshaw_level = self.renshaw.glycinergic_level
        if renshaw_level > 0.0:
            for neuron in self.alpha_mns:
                neuron.receive_inhibition(target_time, renshaw_level)

        self.reciprocal.step_until(target_time)
        reciprocal_level = self.reciprocal.inhibitory_level
        if reciprocal_level > 0.0:
            for neuron in self.alpha_mns:
                neuron.receive_inhibition(target_time, reciprocal_level)

        self._time = target_time
        self._twitch.step_to(target_time)
        self._net_drive = sum(neuron.last_drive for neuron in self.alpha_mns)

    def step_until(self, t_stop: float) -> None:
        self._advance(t_stop)

    # ------------------------------------------------------------------ routing
    def _matches_target(self, target: Optional[str]) -> bool:
        if not target:
            return True
        target_lower = target.lower()
        return target_lower in {self.pool_identifier, self.muscle_name.lower(), self.pool}

    def receive(self, event: MutableMapping[str, object]) -> None:
        time = float(event.get("t", self._time))
        self._advance(time)

        if not self._matches_target(event.get("target")):
            return

        weight = float(event.get("weight", 0.0))
        fiber = str(event.get("fiber", "")).lower()
        source = str(event.get("source", "")).lower()

        if fiber in {"wdr", "i", "iii_iv"} or source == "dorsal_horn":
            self._apply_excitatory_drive(time, weight)
        elif fiber == "ia":
            self._apply_monosynaptic_drive(time, weight)
        elif fiber == "ib":
            self._apply_inhibitory_drive(time, weight)
        elif fiber == "desc" or source == "corticospinal":
            self._apply_descending_drive(time, weight)
        else:
            self._apply_excitatory_drive(time, weight * 0.8)

    # ----------------------------------------------------------------- drive ops
    def _apply_excitatory_drive(self, time: float, weight: float) -> None:
        for idx, neuron in enumerate(self.alpha_mns):
            scale = 0.45 + 0.1 * (len(self.alpha_mns) - idx - 1)
            neuron.receive_excitation(time, weight * scale)
        for neuron in self.gamma_mns:
            neuron.receive_excitation(time, weight * 0.2)

    def _apply_monosynaptic_drive(self, time: float, weight: float) -> None:
        for neuron in self.alpha_mns:
            neuron.receive_excitation(time, weight * 1.4)
        if self.gamma_mns:
            self.gamma_mns[0].receive_excitation(time, weight * 0.5)

    def _apply_inhibitory_drive(self, time: float, weight: float) -> None:
        for neuron in self.alpha_mns:
            neuron.receive_inhibition(time, weight * 1.1)
        for neuron in self.gamma_mns:
            neuron.receive_inhibition(time, weight * 0.3)

    def _apply_descending_drive(self, time: float, weight: float) -> None:
        self._descending_bias += weight
        self._descending_last = time
        self._apply_threshold_offsets()
        for neuron in self.alpha_mns:
            neuron.receive_excitation(time, weight * 0.6)
        for neuron in self.gamma_mns:
            neuron.receive_excitation(time, weight * 0.4)

    # ------------------------------------------------------------------- helpers
    def _record_alpha_spike(self, profile: Dict[str, float], spike_time: float) -> None:
        idx = int(profile["mn_id"])
        if idx < len(self._alpha_recent_spikes):
            self._alpha_recent_spikes[idx] = True
        self.renshaw.receive_spike(spike_time, profile.get("renshaw_weight", 1.0))
        self._twitch.add_spike(
            spike_time,
            profile["mn_id"],
            profile["twitch_amp"],
            profile["tau_c"],
            activation_scale=profile.get("activation_scale"),
        )

        if self._antagonist is not None:
            self._antagonist._receive_antagonist_drive(
                spike_time, profile.get("reciprocal_weight", 1.0)
            )

    # ------------------------------------------------------------------- outputs
    def emit_command(self) -> Optional[MotorCommand]:
        self._advance(self._time)
        if self.anesthesia.is_suspended:
            self._suspended_emit_logged = True
            self._twitch.collect_events()
            return None

        events = self._twitch.collect_events()
        activation = self._twitch.activation
        base_signal = self.pool
        joint_key = "elbow_flexion"
        contraction_key = f"{base_signal}_contraction"
        signals = {
            contraction_key: activation,
            joint_key: activation if "biceps" in self.muscle_name else -activation,
        }
        return MotorCommand(
            t=self._time,
            muscle=self.muscle_name,
            twitch_events=[{"mn_id": ev["mn_id"], "amp": ev["amp"], "tau_c": ev["tau_c"]} for ev in events],
            activation=activation,
            region=self.region,
            signals=signals,
        )

    def telemetry(self) -> MotorPoolState:
        alpha_rates = [mn.firing_rate(self._time, 120.0) for mn in self.alpha_mns]
        gamma_rates = [mn.firing_rate(self._time, 150.0) for mn in self.gamma_mns]
        alpha_spikes = self._alpha_recent_spikes.copy()
        gamma_spikes = self._gamma_recent_spikes.copy()
        self._alpha_recent_spikes = [False] * len(self.alpha_mns)
        self._gamma_recent_spikes = [False] * len(self.gamma_mns)
        return MotorPoolState(
            t=self._time,
            pool=self.pool,
            alpha_rates=alpha_rates,
            alpha_spikes=alpha_spikes,
            gamma_rates=gamma_rates,
            renshaw_level=self.renshaw.glycinergic_level,
            reciprocal_inhibition=self.reciprocal.inhibitory_level,
            net_drive=self._net_drive,
        )

    # ---------------------------------------------------------------- utilities
    def recent_spike_counts(self) -> Iterable[int]:  # pragma: no cover - debug helper
        return [len(mn.spike_times) for mn in self.alpha_mns]

    def _receive_antagonist_drive(self, time: float, weight: float) -> None:
        self.reciprocal.receive_antagonist_spike(time, weight)
        for neuron in self.alpha_mns:
            neuron.receive_inhibition(time, weight * 0.9)


class AnesthesiaController:
    """Shared state that allows pools to be suspended."""

    def __init__(self) -> None:
        self._suspended = False

    def suspend(self) -> None:
        self._suspended = True

    def resume(self) -> None:
        self._suspended = False

    @property
    def is_suspended(self) -> bool:
        return self._suspended
