"""Aggregation utilities for the back musculoskeletal module."""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Sequence

from audit.audit_logger_factory import AuditLoggerFactory

from .bones import BACK_BONES, BackBone
from .muscles import BACK_MUSCLES, BackMuscle
from .stabilizers import BACK_STABILIZERS, BackStabilizer


class BackModule:
    """Package back segments, muscles, and stabilizers for rig export."""

    module_name = "back"

    def __init__(self, *, audit_factory: AuditLoggerFactory | None = None) -> None:
        self.audit = audit_factory or AuditLoggerFactory(self.module_name)
        self._bones: Sequence[BackBone] = tuple(BACK_BONES)
        self._muscles: Sequence[BackMuscle] = tuple(BACK_MUSCLES)
        self._stabilizers: Sequence[BackStabilizer] = tuple(BACK_STABILIZERS)
        self.audit.log_event(
            "init",
            {
                "module": self.module_name,
                "bone_count": len(self._bones),
                "muscle_count": len(self._muscles),
                "stabilizer_count": len(self._stabilizers),
            },
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def bones(self) -> Sequence[BackBone]:  # pragma: no cover - simple property
        return self._bones

    @property
    def muscles(self) -> Sequence[BackMuscle]:  # pragma: no cover - simple property
        return self._muscles

    @property
    def stabilizers(self) -> Sequence[BackStabilizer]:  # pragma: no cover - simple property
        return self._stabilizers

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------
    def log_structure_summary(self) -> None:
        """Emit a readable summary of the configured back components."""

        self.audit.log_event(
            "structure_summary",
            {
                "bones": [bone.name for bone in self._bones],
                "muscles": [muscle.name for muscle in self._muscles],
                "stabilizers": [stabilizer.name for stabilizer in self._stabilizers],
            },
        )

    # ------------------------------------------------------------------
    # Metadata builders
    # ------------------------------------------------------------------
    def build_rig_metadata(self) -> Dict[str, object]:
        """Return serializable metadata for rig driving."""

        metadata: Dict[str, object] = {
            "module": self.module_name,
            "bones": [asdict(bone) for bone in self._bones],
            "muscles": [asdict(muscle) for muscle in self._muscles],
            "stabilizers": [asdict(stabilizer) for stabilizer in self._stabilizers],
        }
        self.audit.log_event(
            "build_rig_metadata",
            {
                "bone_count": len(metadata["bones"]),
                "muscle_count": len(metadata["muscles"]),
                "stabilizer_count": len(metadata["stabilizers"]),
            },
        )
        return metadata

    def build_stability_profile(self) -> Dict[str, object]:
        """Summarize how movement control and passive support interplay."""

        profile = {
            "module": self.module_name,
            "segments": [
                {
                    "name": bone.name,
                    "segment": bone.segment,
                    "degrees_of_freedom": bone.degrees_of_freedom,
                }
                for bone in self._bones
            ],
            "primary_muscles": [
                {
                    "name": muscle.name,
                    "actions": muscle.primary_actions,
                    "stability_role": muscle.stability_role,
                }
                for muscle in self._muscles
            ],
            "passive_support": [
                {
                    "name": stabilizer.name,
                    "attachments": stabilizer.attachments,
                    "stiffness": stabilizer.stiffness,
                    "damping": stabilizer.damping,
                    "feedback": stabilizer.feedback_channels,
                }
                for stabilizer in self._stabilizers
            ],
        }
        self.audit.log_event(
            "build_stability_profile",
            {
                "segment_count": len(profile["segments"]),
                "muscle_count": len(profile["primary_muscles"]),
                "support_count": len(profile["passive_support"]),
            },
        )
        return profile


__all__ = ["BackModule"]