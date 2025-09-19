"""Biophysical dorsal horn network with laminar organisation.

This module provides a small yet expressive simulation of dorsal horn
microcircuits.  The implementation follows a conductance-based leaky
integrate-and-fire (gLIF) abstraction so the neurons react to a combination of
synaptic conductances and applied currents.  Each lamina (I–VI) is represented
with a characteristic neuron and a handful of synapses that model the dominant
inputs described in neurophysiology literature: nociceptive afferents terminate
in laminae I–II, low-threshold mechanoreceptors in laminae III–IV and wide
dynamic range neurons reside in lamina V.  A proprioceptive lamina VI element
anchors the reflex output to the motor pools.

The :func:`process_input` helper exposes a convenient façade that accepts a raw
stimulus intensity (or a configuration mapping) and integrates the circuit over
several milliseconds.  The return value combines symbolic reflex summaries with
spike rasters and membrane traces so higher level reasoning modules can inspect
both abstract decisions (``"withdrawal"``, ``"maintain_contact"`` or
``"no_action"``) and the underlying neurophysiology.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, MutableMapping, Tuple, Union

Number = Union[int, float]


@dataclass
class ConductanceNeuron:
    """Simplified conductance-based leaky integrate-and-fire neuron.

    Parameters
    ----------
    C_m:
        Membrane capacitance in microfarads.
    g_L:
        Leak conductance in microsiemens.
    E_L:
        Leak reversal potential in millivolts.
    V_th:
        Spike threshold in millivolts.
    V_reset:
        Membrane potential after a spike.
    dt:
        Simulation timestep in milliseconds.
    """

    C_m: float
    g_L: float
    E_L: float
    V_th: float
    V_reset: float
    dt: float = 1.0
    name: str = "neuron"
    v: float = field(init=False)
    time: float = field(default=0.0, init=False)
    membrane_trace: List[float] = field(default_factory=list, init=False)
    spike_train: List[bool] = field(default_factory=list, init=False)
    spike_times: List[float] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.v = self.E_L
        self.membrane_trace.append(self.v)

    def step(self, synapses: Iterable["Synapse"], I_in: float = 0.0) -> bool:
        """Advance the membrane potential by one timestep.

        Parameters
        ----------
        synapses:
            Iterable of synapses currently impinging on the neuron.
        I_in:
            Additional applied current (microamperes).

        Returns
        -------
        bool
            ``True`` when the membrane potential crosses the spike threshold.
        """

        total_syn_current = 0.0
        for syn in synapses:
            total_syn_current += syn.current(self.v)

        leak_current = -self.g_L * (self.v - self.E_L)
        dv = (leak_current + total_syn_current + I_in) * (self.dt / self.C_m)
        self.v += dv

        spiked = self.v >= self.V_th
        if spiked:
            self.v = self.V_reset
            self.spike_times.append(self.time)
        self.membrane_trace.append(self.v)
        self.spike_train.append(spiked)
        self.time += self.dt
        return spiked

    def reset(self) -> None:
        """Return the neuron to its resting state."""

        self.v = self.E_L
        self.time = 0.0
        self.membrane_trace = [self.v]
        self.spike_train.clear()
        self.spike_times.clear()


@dataclass
class Synapse:
    """Exponential synapse that tracks conductance in response to spikes."""

    tau: float
    weight: float
    reversal: float
    g: float = 0.0

    def activate(self, spikes: float, modulation: float = 1.0) -> None:
        """Increase the synaptic conductance based on incoming spikes."""

        if spikes <= 0.0:
            return
        self.g += self.weight * modulation * spikes

    def decay(self, dt: float) -> None:
        """Apply exponential decay to the conductance."""

        if self.g <= 0.0:
            return
        self.g *= math.exp(-dt / self.tau)
        if self.g < 1e-9:
            self.g = 0.0

    def current(self, voltage: float) -> float:
        """Return the synaptic current for the provided *voltage*."""

        return self.g * (self.reversal - voltage)

    @property
    def is_inhibitory(self) -> bool:
        """Whether the synapse hyperpolarises the postsynaptic neuron."""

        return self.reversal < -45.0


class AMPASynapse(Synapse):
    """Fast glutamatergic synapse with a 0 mV reversal potential."""

    def __init__(self, weight: float, tau: float = 5.0) -> None:
        super().__init__(tau=tau, weight=weight, reversal=0.0)


class NMDASynapse(Synapse):
    """Slow glutamatergic synapse modelling NMDA receptor kinetics."""

    def __init__(self, weight: float, tau: float = 50.0) -> None:
        super().__init__(tau=tau, weight=weight, reversal=0.0)


class GABAASynapse(Synapse):
    """Fast inhibitory synapse dominated by GABA_A receptors."""

    def __init__(self, weight: float, tau: float = 8.0) -> None:
        super().__init__(tau=tau, weight=weight, reversal=-70.0)


class GABABSynapse(Synapse):
    """Slower metabotropic inhibitory synapse (GABA_B)."""

    def __init__(self, weight: float, tau: float = 120.0) -> None:
        super().__init__(tau=tau, weight=weight, reversal=-95.0)


class GlycineSynapse(Synapse):
    """Spinal glycinergic inhibitory synapse."""

    def __init__(self, weight: float, tau: float = 10.0) -> None:
        super().__init__(tau=tau, weight=weight, reversal=-80.0)


@dataclass
class PoissonFiber:
    """Deterministic approximation of a Poisson spike generator."""

    name: str
    base_rate: float
    gain: float
    threshold: float = 0.0
    saturation: float | None = None

    def rate(self, intensity: float, extra: float = 0.0) -> float:
        """Return the firing rate in Hz for the given *intensity*."""

        drive = max(0.0, intensity - self.threshold)
        rate = self.base_rate + self.gain * drive + extra
        if self.saturation is not None:
            rate = min(rate, self.saturation)
        return max(rate, 0.0)

    def expected_spikes(self, intensity: float, dt: float, extra: float = 0.0) -> float:
        """Return the expected number of spikes during a timestep."""

        rate_hz = self.rate(intensity, extra=extra)
        return rate_hz * (dt / 1000.0)


@dataclass
class AstrocyteModulator:
    """Astrocyte-derived modulation of synaptic gain (wind-up)."""

    threshold: float = 0.05
    potentiation: float = 0.03
    decay: float = 0.97
    level: float = 0.0

    def update(self, c_activity: float) -> float:
        """Update the modulation level based on C-fibre activity."""

        if c_activity > self.threshold:
            self.level = min(1.5, self.level + self.potentiation)
        else:
            self.level *= self.decay
        return 1.0 + self.level

    def summary(self) -> Mapping[str, float]:
        """Return the current astrocytic modulation level."""

        return {"level": self.level}


@dataclass
class DescendingControl:
    """Descending serotonergic/noradrenergic modulation."""

    mode: str = "neutral"
    strength: float = 1.0

    def inhibition_gain(self) -> float:
        """Amount of inhibitory drive delivered to nociceptive laminae."""

        if self.mode == "analgesia":
            return 0.4 * self.strength
        if self.mode == "facilitation":
            return 0.05 * self.strength
        return 0.0

    def facilitation_gain(self) -> float:
        """Amount of excitatory facilitation provided by descending fibres."""

        if self.mode == "facilitation":
            return 0.3 * self.strength
        return 0.0

    def summary(self) -> Mapping[str, Union[str, float]]:
        """Expose a summary dictionary used in :func:`process_input`."""

        return {"mode": self.mode, "strength": self.strength}


class LaminaBase:
    """Base helper used by each lamina implementation."""

    def __init__(self, name: str, neuron: ConductanceNeuron) -> None:
        self.name = name
        self.neuron = neuron
        self.release_history: List[float] = []

    def record_release(self, value: float) -> None:
        self.release_history.append(value)

    def summary(self) -> Mapping[str, object]:
        """Return a dictionary summarising spiking and membrane traces."""

        return {
            "membrane": list(self.neuron.membrane_trace),
            "spikes": list(self.neuron.spike_train),
            "release": list(self.release_history),
        }


class LaminaI(LaminaBase):
    """Projection neurons receiving nociceptive-specific input."""

    def __init__(self, dt: float) -> None:
        super().__init__(
            "I",
            ConductanceNeuron(
                C_m=0.25,
                g_L=0.015,
                E_L=-65.0,
                V_th=-50.0,
                V_reset=-60.0,
                dt=dt,
                name="Lamina I projection",
            ),
        )
        self.a_delta_syn = AMPASynapse(weight=0.08)
        self.c_syn = NMDASynapse(weight=0.07, tau=70.0)
        self.gaba_gate_syn = GABAASynapse(weight=0.05, tau=12.0)
        self.desc_inhib_syn = GABABSynapse(weight=0.04, tau=140.0)
        self.desc_exc_syn = AMPASynapse(weight=0.045, tau=15.0)

    def step(
        self,
        a_delta: float,
        c_input: float,
        gate_level: float,
        descending: DescendingControl,
        astro_gain: float,
    ) -> bool:
        analgesia_scale = 1.0
        if descending.mode == "analgesia":
            analgesia_scale = 1.0 / (1.0 + descending.inhibition_gain())

        scaled_a_delta = a_delta * analgesia_scale
        scaled_c = c_input * analgesia_scale

        if scaled_a_delta > 0.0:
            self.a_delta_syn.activate(scaled_a_delta)
        if scaled_c > 0.0:
            self.c_syn.activate(scaled_c, modulation=astro_gain)
        if gate_level > 0.0:
            self.gaba_gate_syn.activate(gate_level)
        inhibition = descending.inhibition_gain()
        if inhibition > 0.0 and descending.mode != "analgesia":
            self.desc_inhib_syn.activate(min(inhibition, 0.6))
        facilitation = descending.facilitation_gain()
        if facilitation > 0.0:
            self.desc_exc_syn.activate(facilitation)

        synapses = [
            self.a_delta_syn,
            self.c_syn,
            self.gaba_gate_syn,
            self.desc_inhib_syn,
            self.desc_exc_syn,
        ]
        total_exc = self.a_delta_syn.g + self.c_syn.g + self.desc_exc_syn.g
        total_inh = self.gaba_gate_syn.g + self.desc_inhib_syn.g
        spiked = self.neuron.step(synapses=synapses)
        for syn in synapses:
            syn.decay(self.neuron.dt)
        release = 1.0 if spiked else max(0.0, (total_exc - total_inh) * 3.0)
        self.record_release(min(release, 1.5))
        return spiked


class LaminaII(LaminaBase):
    """Inhibitory interneurons providing gate control of nociception."""

    def __init__(self, dt: float) -> None:
        super().__init__(
            "II",
            ConductanceNeuron(
                C_m=0.23,
                g_L=0.012,
                E_L=-66.0,
                V_th=-48.0,
                V_reset=-60.0,
                dt=dt,
                name="Lamina II interneuron",
            ),
        )
        self.c_syn = NMDASynapse(weight=0.06, tau=80.0)
        self.a_delta_syn = AMPASynapse(weight=0.035, tau=10.0)
        self.glycine_output = GlycineSynapse(weight=0.6, tau=18.0)

    def step(self, inputs: Mapping[str, float], astro_gain: float) -> Tuple[bool, float]:
        c_input = inputs.get("C", 0.0)
        a_delta = inputs.get("A_delta", 0.0)
        if c_input > 0.0:
            self.c_syn.activate(c_input, modulation=0.6 + 0.4 * astro_gain)
        if a_delta > 0.0:
            self.a_delta_syn.activate(a_delta * 0.5)

        synapses = [self.c_syn, self.a_delta_syn]
        total_g = sum(s.g for s in synapses)
        spiked = self.neuron.step(synapses=synapses, I_in=0.12)
        for syn in synapses:
            syn.decay(self.neuron.dt)
        release = 0.7 if spiked else max(0.05, total_g * 4.0)
        self.glycine_output.activate(release)
        gate_level = min(self.glycine_output.g, 0.6)
        self.glycine_output.decay(self.neuron.dt)
        self.record_release(min(gate_level, 1.2))
        return spiked, gate_level


class LaminaIIIIV(LaminaBase):
    """Low-threshold mechanoreceptors (Aβ input)."""

    def __init__(self, dt: float) -> None:
        super().__init__(
            "III_IV",
            ConductanceNeuron(
                C_m=0.24,
                g_L=0.012,
                E_L=-65.0,
                V_th=-52.0,
                V_reset=-58.0,
                dt=dt,
                name="Lamina III/IV touch neuron",
            ),
        )
        self.a_beta_syn = AMPASynapse(weight=0.09, tau=6.0)
        self.desc_facilitation = AMPASynapse(weight=0.03, tau=12.0)

    def step(self, a_beta: float, descending: DescendingControl) -> Tuple[bool, float]:
        if a_beta > 0.0:
            self.a_beta_syn.activate(a_beta)
        facilitation = descending.facilitation_gain()
        if facilitation > 0.0:
            self.desc_facilitation.activate(facilitation * 0.3)

        synapses = [self.a_beta_syn, self.desc_facilitation]
        total_g = sum(s.g for s in synapses)
        spiked = self.neuron.step(synapses=synapses)
        for syn in synapses:
            syn.decay(self.neuron.dt)
        release = 1.0 if spiked else max(0.05, total_g * 4.5)
        self.record_release(min(release, 1.5))
        return spiked, release


class LaminaV(LaminaBase):
    """Wide dynamic range neurons integrating nociceptive and mechanoreceptive input."""

    def __init__(self, dt: float) -> None:
        super().__init__(
            "V",
            ConductanceNeuron(
                C_m=0.3,
                g_L=0.016,
                E_L=-65.0,
                V_th=-51.0,
                V_reset=-58.0,
                dt=dt,
                name="Lamina V WDR neuron",
            ),
        )
        self.a_beta_syn = AMPASynapse(weight=0.07, tau=8.0)
        self.a_delta_syn = AMPASynapse(weight=0.065, tau=6.0)
        self.c_syn = NMDASynapse(weight=0.06, tau=80.0)
        self.gaba_gate_syn = GABAASynapse(weight=0.06, tau=14.0)
        self.desc_inhib_syn = GABABSynapse(weight=0.05, tau=150.0)
        self.desc_exc_syn = AMPASynapse(weight=0.05, tau=15.0)
        self.proprio_syn = AMPASynapse(weight=0.045, tau=10.0)

    def step(
        self,
        touch_release: float,
        a_delta: float,
        c_input: float,
        inhibition_level: float,
        descending: DescendingControl,
        astro_gain: float,
        proprio: float,
    ) -> bool:
        if touch_release > 0.0:
            self.a_beta_syn.activate(touch_release)

        analgesia_scale = 1.0
        if descending.mode == "analgesia":
            analgesia_scale = 1.0 / (1.0 + descending.inhibition_gain())

        scaled_a_delta = a_delta * analgesia_scale
        scaled_c = c_input * analgesia_scale

        if scaled_a_delta > 0.0:
            self.a_delta_syn.activate(scaled_a_delta)
        if scaled_c > 0.0:
            self.c_syn.activate(scaled_c, modulation=astro_gain)
        if inhibition_level > 0.0:
            self.gaba_gate_syn.activate(inhibition_level)
        inhibition = descending.inhibition_gain()
        if inhibition > 0.0 and descending.mode != "analgesia":
            self.desc_inhib_syn.activate(min(inhibition * 0.7, 0.6))
        facilitation = descending.facilitation_gain()
        if facilitation > 0.0:
            self.desc_exc_syn.activate(facilitation)
        if proprio > 0.0:
            self.proprio_syn.activate(proprio)

        synapses = [
            self.a_beta_syn,
            self.a_delta_syn,
            self.c_syn,
            self.gaba_gate_syn,
            self.desc_inhib_syn,
            self.desc_exc_syn,
            self.proprio_syn,
        ]
        total_exc = (
            self.a_beta_syn.g
            + self.a_delta_syn.g
            + self.c_syn.g
            + self.desc_exc_syn.g
            + self.proprio_syn.g
        )
        total_inh = self.gaba_gate_syn.g + self.desc_inhib_syn.g
        spiked = self.neuron.step(synapses=synapses)
        for syn in synapses:
            syn.decay(self.neuron.dt)
        release = 1.0 if spiked else max(0.0, (total_exc - total_inh) * 2.5)
        self.record_release(min(release, 1.5))
        return spiked


class LaminaVI(LaminaBase):
    """Proprioceptive relay neurons (lamina VI)."""

    def __init__(self, dt: float) -> None:
        super().__init__(
            "VI",
            ConductanceNeuron(
                C_m=0.28,
                g_L=0.012,
                E_L=-66.0,
                V_th=-53.0,
                V_reset=-60.0,
                dt=dt,
                name="Lamina VI proprioceptive neuron",
            ),
        )
        self.ia_syn = AMPASynapse(weight=0.05, tau=10.0)

    def step(self, ia_input: float) -> bool:
        if ia_input > 0.0:
            self.ia_syn.activate(ia_input)
        synapses = [self.ia_syn]
        total_g = self.ia_syn.g
        spiked = self.neuron.step(synapses=synapses)
        for syn in synapses:
            syn.decay(self.neuron.dt)
        release = 1.0 if spiked else min(1.2, total_g * 5.0)
        self.record_release(release)
        return spiked


class DorsalHornNetwork:
    """Composite dorsal horn network spanning laminae I–VI."""

    def __init__(self, dt: float = 1.0) -> None:
        self.dt = dt
        self.lamina_I = LaminaI(dt)
        self.lamina_II = LaminaII(dt)
        self.lamina_III_IV = LaminaIIIIV(dt)
        self.lamina_V = LaminaV(dt)
        self.lamina_VI = LaminaVI(dt)

    @property
    def laminae(self) -> Mapping[str, LaminaBase]:
        return {
            "I": self.lamina_I,
            "II": self.lamina_II,
            "III_IV": self.lamina_III_IV,
            "V": self.lamina_V,
            "VI": self.lamina_VI,
        }

    def step(
        self,
        fiber_spikes: Mapping[str, float],
        descending: DescendingControl,
        astro_gain: float,
    ) -> None:
        gate_spike, gate_release = self.lamina_II.step(fiber_spikes, astro_gain=astro_gain)
        touch_spike, touch_release = self.lamina_III_IV.step(
            fiber_spikes.get("A_beta", 0.0), descending=descending
        )
        self.lamina_I.step(
            a_delta=fiber_spikes.get("A_delta", 0.0),
            c_input=fiber_spikes.get("C", 0.0),
            gate_level=gate_release,
            descending=descending,
            astro_gain=astro_gain,
        )
        self.lamina_V.step(
            touch_release=touch_release,
            a_delta=fiber_spikes.get("A_delta", 0.0),
            c_input=fiber_spikes.get("C", 0.0),
            inhibition_level=gate_release,
            descending=descending,
            astro_gain=astro_gain,
            proprio=fiber_spikes.get("Ia", 0.0),
        )
        self.lamina_VI.step(fiber_spikes.get("Ia", 0.0))

    def summary(self) -> Mapping[str, Mapping[str, object]]:
        return {name: lamina.summary() for name, lamina in self.laminae.items()}


def _parse_signal(
    signal: Union[Number, Mapping[str, Union[Number, str]]]
) -> Tuple[float, Dict[str, Union[Number, str]]]:
    """Coerce *signal* to an intensity and metadata dictionary."""

    if isinstance(signal, Mapping):
        if "intensity" not in signal:
            raise KeyError("signal mapping must contain an 'intensity' key")
        data = dict(signal)
        intensity = float(data.pop("intensity"))
        return intensity, data
    return float(signal), {}


def process_input(
    signal: Union[Number, Mapping[str, Union[Number, str]]]
) -> MutableMapping[str, object]:
    """Simulate dorsal horn processing for a sensory signal.

    Parameters
    ----------
    signal:
        Either a numeric intensity or a mapping that must contain an
        ``"intensity"`` key.  Optional keys include ``"duration"`` (milliseconds),
        ``"descending"`` (``"neutral"``, ``"analgesia"`` or ``"facilitation"``),
        ``"descending_strength"`` and ``"proprioceptive"`` (biasing Ia input).

    Returns
    -------
    dict
        Structured dictionary containing fibre activity, laminar spike rasters,
        modulation summaries and the reflex interpretation (withdrawal vs.
        maintain contact).
    """

    intensity, extras = _parse_signal(signal)
    dt = float(extras.get("dt", 1.0))
    duration = float(extras.get("duration", 120.0))
    steps = max(1, int(round(duration / dt)))
    descending_mode = str(extras.get("descending", "neutral"))
    descending_strength = float(extras.get("descending_strength", 1.0))
    proprio_bias = float(extras.get("proprioceptive", 0.0))

    descending = DescendingControl(mode=descending_mode, strength=descending_strength)
    network = DorsalHornNetwork(dt=dt)
    astrocyte = AstrocyteModulator()

    fibers = {
        "A_beta": PoissonFiber("Aβ", base_rate=8.0, gain=140.0, threshold=0.1, saturation=220.0),
        "A_delta": PoissonFiber("Aδ", base_rate=0.0, gain=110.0, threshold=0.55, saturation=180.0),
        "C": PoissonFiber("C", base_rate=0.0, gain=90.0, threshold=0.7, saturation=140.0),
        "Ia": PoissonFiber("Ia", base_rate=5.0, gain=60.0, threshold=0.15, saturation=160.0),
    }

    fiber_history: Dict[str, List[float]] = {name: [] for name in fibers}

    for _ in range(steps):
        fiber_spikes: Dict[str, float] = {}
        for key, fiber in fibers.items():
            extra_drive = 0.0
            if key == "Ia" and proprio_bias:
                extra_drive = proprio_bias * 120.0
            expected = fiber.expected_spikes(intensity, dt, extra=extra_drive)
            fiber_history[key].append(expected)
            fiber_spikes[key] = expected

        astro_gain = astrocyte.update(fiber_spikes["C"])
        network.step(fiber_spikes=fiber_spikes, descending=descending, astro_gain=astro_gain)

    lamina_summary = network.summary()

    nociceptive_spikes = sum(lamina_summary["I"]["spikes"])
    wdr_spikes = sum(lamina_summary["V"]["spikes"])
    touch_spikes = sum(lamina_summary["III_IV"]["spikes"])
    proprio_spikes = sum(lamina_summary["VI"]["spikes"])

    wdr_nociceptive_component = max(0.0, wdr_spikes - 0.5 * touch_spikes)
    withdrawal_drive = nociceptive_spikes + 0.6 * wdr_nociceptive_component
    pain_gate = 1.0 / (1.0 + max(nociceptive_spikes, 0.0))
    maintain_drive = (touch_spikes + 0.3 * proprio_spikes) * pain_gate
    inhibition_drive = sum(lamina_summary["II"]["release"])

    if withdrawal_drive >= 1.5 and withdrawal_drive > maintain_drive:
        overall = "withdrawal"
    elif maintain_drive >= 1.0:
        overall = "maintain_contact"
    else:
        overall = "no_action"

    fiber_summary = {
        name: {
            "rate_hz": fibers[name].rate(intensity),
            "total_expected_spikes": sum(history),
            "mean_expected_spikes": sum(history) / len(history),
        }
        for name, history in fiber_history.items()
    }

    result: MutableMapping[str, object] = {
        "stimulus": {
            "intensity": intensity,
            "duration_ms": duration,
            "dt_ms": dt,
        },
        "fibers": fiber_summary,
        "laminae": lamina_summary,
        "spike_raster": {name: data["spikes"] for name, data in lamina_summary.items()},
        "modulation": {
            "astrocyte": astrocyte.summary(),
            "descending": descending.summary(),
        },
        "reflexes": {
            "withdrawal": withdrawal_drive,
            "maintain_contact": maintain_drive,
            "suppression": inhibition_drive,
        },
        "overall": overall,
    }

    return result


__all__ = [
    "ConductanceNeuron",
    "Synapse",
    "AMPASynapse",
    "NMDASynapse",
    "GABAASynapse",
    "GABABSynapse",
    "GlycineSynapse",
    "PoissonFiber",
    "AstrocyteModulator",
    "DescendingControl",
    "DorsalHornNetwork",
    "process_input",
]
