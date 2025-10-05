"""Symbolic cardiac rhythm generator with reflex integration hooks."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Mapping, MutableMapping, Optional, Tuple, Union, TYPE_CHECKING

from audit.audit_logger_factory import AuditLoggerFactory

try:  # pragma: no cover - optional dependency during tests
    from spinal_cord.signal_registry import REFLEX_INDEX
except Exception:  # pragma: no cover - allow standalone usage
    REFLEX_INDEX = None  # type: ignore[assignment]

if TYPE_CHECKING:  # pragma: no cover - type checking helper
    from limbic_system.emotion import EmotionState
else:  # pragma: no cover - runtime fallback when limbic system is absent
    EmotionState = Any  # type: ignore[misc,assignment]


def _clamp(value: float, lower: float, upper: float) -> float:
    """Return *value* constrained to the inclusive ``[lower, upper]`` range."""

    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


@dataclass(frozen=True)
class CardiacPacket:
    """Structured heartbeat sample emitted each simulation tick."""

    pulse_signal: float
    heart_rate_current: float
    bp_systolic: float
    bp_diastolic: float
    phase: str

    def as_dict(self) -> Dict[str, Union[float, str]]:
        """Return a JSON/export friendly representation."""

        return {
            "pulse_signal": self.pulse_signal,
            "heart_rate_current": self.heart_rate_current,
            "bp_systolic": self.bp_systolic,
            "bp_diastolic": self.bp_diastolic,
            "phase": self.phase,
        }


class OrganModuleBase:
    """Lightweight base that mirrors reflex/audit behaviour used by limbs."""

    module_name: str = "organ"
    reflex_subsystem: Optional[str] = None

    def __init__(
        self,
        *,
        audit_factory: Optional[AuditLoggerFactory] = None,
        audit_enabled: bool = True,
    ) -> None:
        self._audit_enabled = audit_enabled
        self.audit = audit_factory or AuditLoggerFactory(self.module_name)
        self._reflex_metadata = self._load_reflex_metadata()
        self._log_event(
            "init",
            {
                "module": self.module_name,
                "reflex_subsystem": self.reflex_subsystem,
                "reflex_count": len(self._reflex_metadata),
                "audit_enabled": self._audit_enabled,
            },
        )

    # ------------------------------------------------------------------
    # Audit helpers
    # ------------------------------------------------------------------
    @property
    def audit_enabled(self) -> bool:
        return self._audit_enabled

    def _log_event(self, event_type: str, data: Mapping[str, Any]) -> None:
        if not self._audit_enabled:
            return
        self.audit.log_event(event_type, dict(data))

    # ------------------------------------------------------------------
    # Reflex metadata access
    # ------------------------------------------------------------------
    def _load_reflex_metadata(self) -> MutableMapping[str, Mapping[str, Any]]:
        if not self.reflex_subsystem or REFLEX_INDEX is None:
            return {}

        try:
            arcs = REFLEX_INDEX.get_by_subsystem(self.reflex_subsystem)
        except Exception:  # pragma: no cover - registry lookup failures are non-fatal
            return {}

        return {
            arc.name: {
                "stimulus": arc.get("stimulus"),
                "afferent": arc.get("afferent"),
                "integration": arc.get("integration"),
                "efferent": arc.get("efferent"),
                "response_type": arc.get("response_type"),
                "source_file": str(getattr(arc.source_file, "name", "")),
            }
            for arc in arcs
        }

    @property
    def reflex_metadata(self) -> Mapping[str, Mapping[str, Any]]:
        return self._reflex_metadata


class HeartModule(OrganModuleBase):
    """Generate symbolic heartbeat and pressure signals for downstream systems."""

    module_name = "heart"
    reflex_subsystem = "cardiac_autonomic"

    def __init__(
        self,
        *,
        rest_rate_bpm: float = 72.0,
        tension_scale: float = 1.0,
        fatigue_scale: float = 1.0,
        amplitude: float = 1.0,
        coherence: float = 0.95,
        systolic_base: float = 120.0,
        diastolic_base: float = 80.0,
        variability: float = 0.03,
        audit_factory: Optional[AuditLoggerFactory] = None,
        audit_enabled: bool = True,
        respiratory_phase_offset: float = 0.25,
    ) -> None:
        self.rest_rate_bpm = float(rest_rate_bpm)
        self._tension_range: Tuple[float, float] = (0.6, 2.2)
        self._fatigue_range: Tuple[float, float] = (0.8, 1.0)
        self.tension_scale = _clamp(float(tension_scale), *self._tension_range)
        self.fatigue_scale = _clamp(float(fatigue_scale), *self._fatigue_range)
        self.amplitude = max(0.1, float(amplitude))
        self.coherence = _clamp(float(coherence), 0.0, 0.999)
        self.systolic_base = float(systolic_base)
        self.diastolic_base = float(diastolic_base)
        self.variability = abs(float(variability))
        self.respiratory_phase_offset = float(respiratory_phase_offset) % 1.0

        self._current_rate_bpm = self.rest_rate_bpm * self.tension_scale * self.fatigue_scale
        self._pulse_phase = 0.0
        self._last_time: Optional[float] = None
        self._last_packet: Optional[CardiacPacket] = None
        self._emotion_factor = 1.0
        self._tension_state = self.tension_scale
        self._fatigue_state = self.fatigue_scale

        super().__init__(audit_factory=audit_factory, audit_enabled=audit_enabled)
        self._log_event(
            "configuration",
            {
                "rest_rate_bpm": self.rest_rate_bpm,
                "tension_scale": self.tension_scale,
                "fatigue_scale": self.fatigue_scale,
                "amplitude": self.amplitude,
                "coherence": self.coherence,
                "systolic_base": self.systolic_base,
                "diastolic_base": self.diastolic_base,
                "variability": self.variability,
                "respiratory_phase_offset": self.respiratory_phase_offset,
            },
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_heartbeat_signal(
        self,
        time_s: float,
        tension: float = 0.0,
        fatigue: float = 0.0,
        *,
        emotion_modulation: Union["EmotionState", Mapping[str, float], None] = None,
        respiration_phase: Optional[float] = None,
    ) -> Dict[str, Union[float, str]]:
        """Return a symbolic heartbeat packet for the current simulation tick."""

        packet = self.generate_heartbeat_packet(
            time_s,
            tension_input=tension,
            fatigue_input=fatigue,
            emotion_modulation=emotion_modulation,
            respiration_phase=respiration_phase,
        )
        return packet.as_dict()

    def generate_heartbeat_packet(
        self,
        time_s: float,
        *,
        tension_input: float = 0.0,
        fatigue_input: float = 0.0,
        emotion_modulation: Union["EmotionState", Mapping[str, float], None] = None,
        respiration_phase: Optional[float] = None,
    ) -> CardiacPacket:
        """Compute the cardiac waveform and vitals at ``time_s``."""

        dt = 0.0 if self._last_time is None else max(0.0, float(time_s) - self._last_time)
        self._last_time = float(time_s)

        self._tension_state = self._resolve_tension_multiplier(tension_input)
        self._fatigue_state = self._resolve_fatigue_multiplier(fatigue_input)
        emotion_factor = self._resolve_emotion_multiplier(emotion_modulation)

        # Blend emotion separately so sudden spikes remain smooth but responsive.
        self._emotion_factor = self._blend(self._emotion_factor, emotion_factor, self.coherence)

        target_rate = self.rest_rate_bpm * self._tension_state * self._fatigue_state * self._emotion_factor
        self._current_rate_bpm = self._blend(self._current_rate_bpm, target_rate, self.coherence)

        frequency_hz = max(0.1, self._current_rate_bpm / 60.0)
        phase_increment = 2.0 * math.pi * frequency_hz * dt
        self._pulse_phase = (self._pulse_phase + phase_increment) % (2.0 * math.pi)

        if respiration_phase is not None:
            phase_target = ((float(respiration_phase) % 1.0) + self.respiratory_phase_offset) % 1.0
            phase_target_rad = phase_target * 2.0 * math.pi
            delta = math.atan2(
                math.sin(phase_target_rad - self._pulse_phase),
                math.cos(phase_target_rad - self._pulse_phase),
            )
            self._pulse_phase = (self._pulse_phase + delta * 0.1) % (2.0 * math.pi)

        phase = (self._pulse_phase + 2.0 * math.pi * self.respiratory_phase_offset) % (2.0 * math.pi)
        pulse_raw = 0.5 * (1.0 + math.sin(phase))
        pulse_signal = _clamp(pulse_raw * self.amplitude, 0.0, 1.0)

        variability_term = math.sin(phase + self._last_time * 0.5) * self.variability
        systolic = (self.systolic_base + (self._tension_state - 1.0) * 20.0) * (1.0 + variability_term)
        diastolic = (self.diastolic_base + (self._tension_state - 1.0) * 10.0) * (1.0 - variability_term * 0.5)
        systolic *= self._fatigue_state
        diastolic *= self._fatigue_state

        phase_label = "systole" if math.sin(phase) >= 0 else "diastole"

        packet = CardiacPacket(
            pulse_signal=pulse_signal,
            heart_rate_current=self._current_rate_bpm,
            bp_systolic=systolic,
            bp_diastolic=diastolic,
            phase=phase_label,
        )
        self._last_packet = packet

        self._log_event(
            "heartbeat",
            {
                "time": self._last_time,
                "pulse_signal": pulse_signal,
                "heart_rate": self._current_rate_bpm,
                "bp_systolic": systolic,
                "bp_diastolic": diastolic,
                "phase": phase_label,
                "tension_multiplier": self._tension_state,
                "fatigue_multiplier": self._fatigue_state,
                "emotion_factor": self._emotion_factor,
            },
        )

        return packet

    # ------------------------------------------------------------------
    # Integration helpers
    # ------------------------------------------------------------------
    @property
    def afferent_channels(self) -> Tuple[str, ...]:
        return "bp_systolic", "bp_diastolic", "heart_rate_current", "pulse_signal"

    @property
    def efferent_channels(self) -> Tuple[str, ...]:
        return "tension_input", "fatigue_input", "emotion_modulation"

    def last_packet(self) -> Optional[Dict[str, Union[float, str]]]:
        return None if self._last_packet is None else self._last_packet.as_dict()

    def build_rig_metadata(self) -> Dict[str, Any]:
        """Return export metadata consumed by ``export_all`` style pipelines."""

        metadata = {
            "module": self.module_name,
            "reflex_subsystem": self.reflex_subsystem,
            "parameters": {
                "rest_rate_bpm": self.rest_rate_bpm,
                "systolic_base": self.systolic_base,
                "diastolic_base": self.diastolic_base,
                "variability": self.variability,
            },
            "rig_channels": [
                {
                    "name": "CTRL_Torso_Heartbeat",
                    "limits": [0.0, float(self.amplitude)],
                    "description": "Normalized cardiac pulse signal",
                }
            ],
            "afferents": self.afferent_channels,
            "efferents": self.efferent_channels,
            "audit_info": {
                "exports_from": "heart_main.py",
                "audit_enabled": self.audit_enabled,
            },
        }
        self._log_event("build_rig_metadata", metadata)
        return metadata

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _resolve_tension_multiplier(self, tension_input: float) -> float:
        target = self.tension_scale + float(tension_input)
        return _clamp(target, *self._tension_range)

    def _resolve_fatigue_multiplier(self, fatigue_input: float) -> float:
        target = self.fatigue_scale - float(fatigue_input)
        return _clamp(target, *self._fatigue_range)

    @staticmethod
    def _resolve_emotion_multiplier(
            emotion_modulation: Union["EmotionState", Mapping[str, float], None],
    ) -> float:
        if emotion_modulation is None:
            return 1.0

        if hasattr(emotion_modulation, "arousal"):
            arousal = float(getattr(emotion_modulation, "arousal", 0.5))
            dominance = float(getattr(emotion_modulation, "dominance", 0.5))
            valence = float(getattr(emotion_modulation, "valence", 0.0))
        else:
            arousal = float(emotion_modulation.get("arousal", 0.5))
            dominance = float(emotion_modulation.get("dominance", 0.5))
            valence = float(emotion_modulation.get("valence", 0.0))

        arousal_effect = 1.0 + (arousal - 0.5) * 0.8
        dominance_effect = 1.0 + (dominance - 0.5) * 0.3
        # Negative valence with high arousal tends to accelerate the heart.
        valence_effect = 1.0 + (-valence) * 0.15

        return _clamp(arousal_effect * dominance_effect * valence_effect, 0.7, 1.6)

    @staticmethod
    def _blend(current: float, target: float, coherence: float) -> float:
        blend = _clamp(coherence, 0.0, 0.999)
        return current * blend + target * (1.0 - blend)


__all__ = ["HeartModule", "OrganModuleBase", "CardiacPacket"]