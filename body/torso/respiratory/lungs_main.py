"""Procedural breathing oscillator for the torso."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Mapping, Optional

from audit.audit_logger_factory import AuditLoggerFactory


@dataclass(frozen=True)
class RespiratorySignalDescriptor:
    """Metadata for a published respiratory signal."""

    path: str
    description: str
    units: str = "normalized"


class RespiratoryModuleBase:
    """Shared helpers for respiratory rhythm generators."""

    module_name: str = "respiratory"
    reflex_subsystem: str = "respiratory_autonomic"
    _afferent_signals: tuple[str, ...] = (
        "breathing_signal",
        "breath_rate_current",
        "breath_phase",
        "breath_velocity",
    )
    _efferent_inputs: tuple[str, ...] = ("tension_input", "emotion_modulation")

    def __init__(
        self,
        *,
        audit_factory: Optional[AuditLoggerFactory] = None,
        audit_enabled: bool = True,
    ) -> None:
        self.audit_enabled = audit_enabled
        self.audit = audit_factory or (AuditLoggerFactory(self.module_name) if audit_enabled else None)
        self._last_packet: Optional[Mapping[str, object]] = None
        self._rig_channels: tuple[Mapping[str, object], ...] = ()
        self._signal_descriptors: tuple[RespiratorySignalDescriptor, ...] = ()

        self._log_event(
            "init",
            {
                "module": self.module_name,
                "reflex_subsystem": self.reflex_subsystem,
                "afferent": self.afferent_signals,
                "efferent": self.efferent_inputs,
            },
        )

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------
    def _log_event(self, event_type: str, payload: Mapping[str, object]) -> None:
        if self.audit_enabled and self.audit is not None:
            self.audit.log_event(event_type, dict(payload))

    # ------------------------------------------------------------------
    # Interface reporting
    # ------------------------------------------------------------------
    @property
    def afferent_signals(self) -> tuple[str, ...]:  # pragma: no cover - simple property
        return self._afferent_signals

    @property
    def efferent_inputs(self) -> tuple[str, ...]:  # pragma: no cover - simple property
        return self._efferent_inputs

    @property
    def rig_channels(self) -> tuple[Mapping[str, object], ...]:  # pragma: no cover - simple property
        return self._rig_channels

    @property
    def signal_descriptors(self) -> tuple[RespiratorySignalDescriptor, ...]:  # pragma: no cover - simple property
        return self._signal_descriptors

    def build_export_metadata(self) -> Dict[str, object]:
        """Package metadata for exporters and registries."""

        metadata: Dict[str, object] = {
            "module": self.module_name,
            "reflex_subsystem": self.reflex_subsystem,
            "parameters": self.parameter_snapshot(),
            "afferent_signals": list(self.afferent_signals),
            "efferent_inputs": list(self.efferent_inputs),
            "rig_channels": [dict(channel) for channel in self.rig_channels],
        }
        if self._last_packet is not None:
            metadata["last_packet"] = dict(self._last_packet)
        if self._signal_descriptors:
            metadata["signal_descriptors"] = [descriptor.__dict__ for descriptor in self._signal_descriptors]
        return metadata

    # ------------------------------------------------------------------
    # Hooks for subclasses
    # ------------------------------------------------------------------
    def parameter_snapshot(self) -> Mapping[str, object]:  # pragma: no cover - to be overridden
        return {}

    def update(
        self,
        time_s: float,
        *,
        tension_input: float = 0.0,
        emotion_modulation: float = 0.0,
    ) -> Mapping[str, object]:
        """Generate the latest respiratory packet."""

        raise NotImplementedError

    def get_breath_signal(self, time_s: float, *, tension: float = 0.0) -> float:
        """Convenience wrapper returning only the normalized breathing signal."""

        packet = self.update(time_s, tension_input=tension)
        value = float(packet["breathing_signal"])
        return max(0.0, min(1.0, value))

    def build_afferent_packet(
        self,
        time_s: float,
        *,
        tension_input: float = 0.0,
        emotion_modulation: float = 0.0,
    ) -> Dict[str, object]:
        """Return a registry-ready payload keyed by reflex path."""

        packet = self.update(time_s, tension_input=tension_input, emotion_modulation=emotion_modulation)
        base_path = f"{self.reflex_subsystem}.{self.module_name}"
        return {
            f"{base_path}.breathing_signal": packet["breathing_signal"],
            f"{base_path}.breathing_signal_scaled": packet["breathing_signal_scaled"],
            f"{base_path}.breath_rate_current": packet["breath_rate_current"],
            f"{base_path}.breath_phase": packet["breath_phase"],
            f"{base_path}.breath_velocity": packet["breath_velocity"],
        }


class LungsModule(RespiratoryModuleBase):
    """Emit a smooth breathing waveform for downstream systems."""

    def __init__(
        self,
        *,
        rest_rate_bpm: float = 15.0,
        tension_scale: float = 1.0,
        amplitude: float = 1.0,
        coherence: float = 0.9,
        inhale_exhale_ratio: float = 0.45,
        phase_offset: float = 0.0,
        audit_enabled: bool = True,
        audit_factory: Optional[AuditLoggerFactory] = None,
    ) -> None:
        super().__init__(audit_factory=audit_factory, audit_enabled=audit_enabled)
        self.rest_rate_bpm = max(1.0, float(rest_rate_bpm))
        self.tension_scale = max(0.1, float(tension_scale))
        self.amplitude = max(0.0, float(amplitude))
        self.coherence = min(0.999, max(0.0, float(coherence)))
        self.inhale_exhale_ratio = min(0.95, max(0.05, float(inhale_exhale_ratio)))
        self.phase_offset = float(phase_offset)
        self._rig_channels = (
            {
                "name": "CTRL_Torso_Breath",
                "limits": (0.0, 1.0),
                "units": "normalized",
                "description": "Primary torso breathing control driven by lungs module.",
            },
        )

        self._smoothed_rate_bpm = self.rest_rate_bpm
        self._cycle_position = (self.phase_offset / (2.0 * math.pi)) % 1.0
        self._last_time: Optional[float] = None
        self._last_signal: Optional[float] = None
        self._last_packet = None
        self._last_phase: Optional[str] = None
        self._cycle_count = 0

        self._log_event(
            "configure",
            {
                "rest_rate_bpm": self.rest_rate_bpm,
                "tension_scale": self.tension_scale,
                "amplitude": self.amplitude,
                "coherence": self.coherence,
                "inhale_exhale_ratio": self.inhale_exhale_ratio,
                "phase_offset": self.phase_offset,
                "rig_channels": [channel["name"] for channel in self._rig_channels],
            },
        )

        base_path = f"{self.reflex_subsystem}.{self.module_name}"
        self._signal_descriptors = (
            RespiratorySignalDescriptor(
                path=f"{base_path}.breathing_signal",
                description="Normalized 0-1 breathing oscillator amplitude.",
            ),
            RespiratorySignalDescriptor(
                path=f"{base_path}.breathing_signal_scaled",
                description="Breathing oscillator with amplitude scaling applied.",
            ),
            RespiratorySignalDescriptor(
                path=f"{base_path}.breath_rate_current",
                description="Current respiratory rate in breaths per minute.",
                units="breaths/minute",
            ),
            RespiratorySignalDescriptor(
                path=f"{base_path}.breath_phase",
                description="Discrete inhale/exhale state derived from the waveform.",
                units="phase",
            ),
            RespiratorySignalDescriptor(
                path=f"{base_path}.breath_velocity",
                description="Rate of change of the normalized breathing signal.",
                units="1/s",
            ),
        )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def parameter_snapshot(self) -> Mapping[str, object]:
        return {
            "rest_rate_bpm": self.rest_rate_bpm,
            "tension_scale": self.tension_scale,
            "amplitude": self.amplitude,
            "coherence": self.coherence,
            "inhale_exhale_ratio": self.inhale_exhale_ratio,
            "phase_offset": self.phase_offset,
        }

    # ------------------------------------------------------------------
    # Internal mechanics
    # ------------------------------------------------------------------
    def _resolve_rate(self, tension_input: float, emotion_modulation: float) -> float:
        target_rate = self.rest_rate_bpm

        if tension_input:
            target_rate *= 1.0 + max(-1.0, min(1.0, tension_input)) * (self.tension_scale - 1.0)
        if emotion_modulation:
            target_rate *= max(0.1, 1.0 + emotion_modulation)

        self._smoothed_rate_bpm = self.coherence * self._smoothed_rate_bpm + (1.0 - self.coherence) * target_rate
        return max(1.0, self._smoothed_rate_bpm)

    def _advance_cycle(self, dt: float, frequency_hz: float) -> None:
        if dt <= 0.0 or not math.isfinite(dt):
            return
        previous_position = self._cycle_position
        self._cycle_position = (self._cycle_position + dt * frequency_hz) % 1.0
        if self._cycle_position < previous_position:
            self._cycle_count += 1
            self._log_event(
                "cycle_start",
                {
                    "cycle": self._cycle_count,
                    "rate_bpm": self._smoothed_rate_bpm,
                },
            )

    def _compute_waveform(self) -> tuple[float, str]:
        phase_ratio = self.inhale_exhale_ratio
        if self._cycle_position < phase_ratio:
            local_phase = self._cycle_position / phase_ratio if phase_ratio > 0.0 else 0.0
            signal = 0.5 * (1.0 - math.cos(math.pi * local_phase))
            phase = "inhale"
        else:
            denom = max(1e-6, 1.0 - phase_ratio)
            local_phase = (self._cycle_position - phase_ratio) / denom
            signal = 0.5 * (1.0 + math.cos(math.pi * local_phase))
            phase = "exhale"
        return signal, phase

    def update(
        self,
        time_s: float,
        *,
        tension_input: float = 0.0,
        emotion_modulation: float = 0.0,
    ) -> Mapping[str, object]:
        if not math.isfinite(time_s):
            raise ValueError("time_s must be a finite float")

        rate_bpm = self._resolve_rate(tension_input, emotion_modulation)
        frequency_hz = rate_bpm / 60.0

        if self._last_time is None:
            dt = 0.0
        else:
            dt = max(0.0, time_s - self._last_time)
        self._advance_cycle(dt, frequency_hz)
        raw_signal, breath_phase = self._compute_waveform()

        signal = raw_signal
        if self._last_signal is not None:
            blend = 0.5 * self.coherence
            signal = (1.0 - blend) * raw_signal + blend * self._last_signal

        scaled_signal = max(0.0, min(1.0, signal * self.amplitude))
        if dt > 0.0:
            velocity = (signal - (self._last_signal if self._last_signal is not None else signal)) / dt
        else:
            velocity = 0.0

        packet: Dict[str, object] = {
            "breathing_signal": max(0.0, min(1.0, signal)),
            "breathing_signal_scaled": scaled_signal,
            "breath_rate_current": rate_bpm,
            "breath_phase": breath_phase,
            "breath_velocity": velocity,
        }

        if breath_phase != self._last_phase:
            self._log_event(
                "phase_transition",
                {
                    "phase": breath_phase,
                    "cycle_position": self._cycle_position,
                    "rate_bpm": rate_bpm,
                },
            )
            self._last_phase = breath_phase

        self._last_packet = packet
        self._last_time = time_s
        self._last_signal = signal

        return packet


__all__ = ["LungsModule", "RespiratoryModuleBase", "RespiratorySignalDescriptor"]