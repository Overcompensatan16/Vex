"""Shared infrastructure for limb routing modules."""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional

from audit.audit_logger_factory import AuditLoggerFactory

try:  # pragma: no cover - fallback for stripped installs
    from spinal_cord.signal_registry import REFLEX_INDEX
except Exception:  # pragma: no cover
    REFLEX_INDEX = None


@dataclass(frozen=True)
class BoneSegment:
    """Simplified bone representation for rig export."""

    name: str
    rig_target: str
    length_cm: float
    parent: Optional[str] = None
    degrees_of_freedom: tuple[str, ...] = ()
    notes: str = ""


@dataclass(frozen=True)
class Joint:
    """Joint articulation metadata."""

    name: str
    bones: tuple[str, str]
    rig_controls: tuple[str, ...]
    limits_deg: tuple[float, float]
    default_pose: float = 0.0
    notes: str = ""


@dataclass(frozen=True)
class MuscleGroup:
    """Motor grouping driving a joint or segment."""

    name: str
    actuators: tuple[str, ...]
    primary_function: str
    fiber_type: str
    notes: str = ""


@dataclass(frozen=True)
class SensorCluster:
    """Sensor bundle contributing afferent feedback."""

    name: str
    sensor_type: str
    afferents: tuple[str, ...]
    rig_notes: str = ""


@dataclass(frozen=True)
class RigChannel:
    """Output channel metadata for rig integration."""

    name: str
    channel_type: str
    default: float = 0.0
    limits: tuple[float, float] | None = None
    units: str = "normalized"
    description: str = ""


@dataclass(frozen=True)
class MicroMovementProfile:
    """Procedural micromotion descriptor."""

    name: str
    target: str
    axis: str
    amplitude: float
    frequency_hz: float
    phase: float = 0.0
    baseline: float = 0.0
    tension_scale: float = 0.0
    breathing_scale: float = 0.0
    description: str = ""

    def sample(
        self,
        time_s: float,
        *,
        tension: float = 0.0,
        breathing: float = 0.0,
    ) -> float:
        """Return a signed offset for the configured target."""

        amplitude = self.amplitude * (
            1.0 + max(0.0, tension) * self.tension_scale + max(0.0, breathing) * self.breathing_scale
        )
        return self.baseline + amplitude * math.sin(2.0 * math.pi * self.frequency_hz * time_s + self.phase)


class LimbModuleBase:
    """Common behaviour for limb routing modules."""

    module_name: str = "limb"
    reflex_subsystem: Optional[str] = None

    def __init__(self, *, audit_factory: Optional[AuditLoggerFactory] = None) -> None:
        self.audit = audit_factory or AuditLoggerFactory(self.module_name)
        self._reflex_metadata = self._load_reflex_metadata()
        self.audit.log_event(
            "init",
            {
                "module": self.module_name,
                "reflex_subsystem": self.reflex_subsystem,
                "reflex_count": len(self._reflex_metadata),
            },
        )

    # ------------------------------------------------------------------
    # Metadata helpers
    # ------------------------------------------------------------------
    @property
    def bones(self) -> List[BoneSegment]:  # pragma: no cover - simple property
        return getattr(self, "_bones", [])

    @property
    def joints(self) -> List[Joint]:  # pragma: no cover - simple property
        return getattr(self, "_joints", [])

    @property
    def muscles(self) -> List[MuscleGroup]:  # pragma: no cover - simple property
        return getattr(self, "_muscles", [])

    @property
    def sensors(self) -> List[SensorCluster]:  # pragma: no cover - simple property
        return getattr(self, "_sensors", [])

    @property
    def rig_channels(self) -> List[RigChannel]:  # pragma: no cover - simple property
        return getattr(self, "_rig_channels", [])

    @property
    def micromovements(self) -> List[MicroMovementProfile]:  # pragma: no cover - simple property
        return getattr(self, "_micromovements", [])

    def log_structure_summary(self) -> None:
        """Emit a concise summary to the audit trail."""

        self.audit.log_event(
            "structure_summary",
            {
                "bones": [bone.name for bone in self.bones],
                "joints": [joint.name for joint in self.joints],
                "muscles": [muscle.name for muscle in self.muscles],
                "sensors": [sensor.name for sensor in self.sensors],
                "rig_channels": [channel.name for channel in self.rig_channels],
                "micromovements": [profile.name for profile in self.micromovements],
            },
        )

    def build_rig_metadata(self) -> Dict[str, Iterable[Mapping[str, object]]]:
        """Compile metadata dictionaries for rig exporters."""

        return {
            "module": self.module_name,
            "reflex_subsystem": self.reflex_subsystem,
            "reflex_metadata": self._reflex_metadata,
            "bones": [asdict(bone) for bone in self.bones],
            "joints": [asdict(joint) for joint in self.joints],
            "muscles": [asdict(muscle) for muscle in self.muscles],
            "sensors": [asdict(sensor) for sensor in self.sensors],
            "rig_channels": [asdict(channel) for channel in self.rig_channels],
            "micromovements": [asdict(profile) for profile in self.micromovements],
        }

    def generate_idle_packet(
        self,
        time_s: float,
        *,
        tension: float = 0.0,
        breathing: float = 0.0,
        overrides: Optional[Mapping[str, float]] = None,
    ) -> Dict[str, Mapping[str, float]]:
        """Compute micromovement offsets with optional overrides."""

        packet: Dict[str, float] = {}
        for profile in self.micromovements:
            value = profile.sample(time_s, tension=tension, breathing=breathing)
            packet[profile.target] = packet.get(profile.target, 0.0) + value

        if overrides:
            packet.update(overrides)

        self.audit.log_event(
            "idle_packet",
            {
                "time": time_s,
                "tension": tension,
                "breathing": breathing,
                "targets": packet,
            },
        )
        return {"module": self.module_name, "channels": packet}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_reflex_metadata(self) -> MutableMapping[str, Mapping[str, object]]:
        if not self.reflex_subsystem or REFLEX_INDEX is None:
            return {}

        arcs = REFLEX_INDEX.get_by_subsystem(self.reflex_subsystem)
        return {
            arc.name: {
                "stimulus": arc.get("stimulus"),
                "afferent": arc.get("afferent"),
                "integration": arc.get("integration"),
                "efferent": arc.get("efferent"),
                "response_type": arc.get("response_type"),
                "source_file": str(arc.source_file.name),
            }
            for arc in arcs
        }


__all__ = [
    "BoneSegment",
    "Joint",
    "MuscleGroup",
    "SensorCluster",
    "RigChannel",
    "MicroMovementProfile",
    "LimbModuleBase",
]