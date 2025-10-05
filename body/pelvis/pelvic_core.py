"""Core pelvic routing and signal integration module."""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Sequence

from audit.audit_logger_factory import AuditLoggerFactory

from .endocrine.limbic_coupling import LimbicCoupling, LIMBIC_COUPLINGS
from .endocrine.reproductive_hormones import ReproductiveHormone, REPRODUCTIVE_HORMONES
from .sensory.pelvic_nerves import PelvicNerve, PELVIC_NERVES
from .sensory.visceral_feedback import VisceralSignal, VISCERAL_FEEDBACK_CHANNELS
from .skeletal.hip_joint_module import PelvicJoint, PELVIC_JOINTS
from .skeletal.pelvic_floor_muscles import PelvicFloorMuscle, PELVIC_FLOOR_MUSCLES
from .skeletal.pelvis_bone_structure import PelvicBone, VaginalStructure, PELVIC_BONES, VAGINAL_STRUCTURE


class PelvisModule:
    """Aggregate pelvic structures and provide sexual-function insights."""

    module_name = "pelvis"

    def __init__(self, *, audit_factory: AuditLoggerFactory | None = None) -> None:
        self.audit = audit_factory or AuditLoggerFactory(self.module_name)
        self._bones: Sequence[PelvicBone] = tuple(PELVIC_BONES)
        self._joints: Sequence[PelvicJoint] = tuple(PELVIC_JOINTS)
        self._muscles: Sequence[PelvicFloorMuscle] = tuple(PELVIC_FLOOR_MUSCLES)
        self._nerves: Sequence[PelvicNerve] = tuple(PELVIC_NERVES)
        self._visceral_channels: Sequence[VisceralSignal] = tuple(VISCERAL_FEEDBACK_CHANNELS)
        self._hormones: Sequence[ReproductiveHormone] = tuple(REPRODUCTIVE_HORMONES)
        self._limbic_couplings: Sequence[LimbicCoupling] = tuple(LIMBIC_COUPLINGS)
        self._vaginal_structure: VaginalStructure = VAGINAL_STRUCTURE
        self.audit.log_event(
            "init",
            {
                "module": self.module_name,
                "bone_count": len(self._bones),
                "joint_count": len(self._joints),
                "muscle_count": len(self._muscles),
                "nerve_count": len(self._nerves),
                "visceral_channel_count": len(self._visceral_channels),
                "hormone_count": len(self._hormones),
                "limbic_coupling_count": len(self._limbic_couplings),
            },
        )

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------
    @property
    def bones(self) -> Sequence[PelvicBone]:  # pragma: no cover - simple property
        return self._bones

    @property
    def joints(self) -> Sequence[PelvicJoint]:  # pragma: no cover - simple property
        return self._joints

    @property
    def muscles(self) -> Sequence[PelvicFloorMuscle]:  # pragma: no cover - simple property
        return self._muscles

    @property
    def nerves(self) -> Sequence[PelvicNerve]:  # pragma: no cover - simple property
        return self._nerves

    @property
    def visceral_channels(self) -> Sequence[VisceralSignal]:  # pragma: no cover - simple property
        return self._visceral_channels

    @property
    def hormones(self) -> Sequence[ReproductiveHormone]:  # pragma: no cover - simple property
        return self._hormones

    @property
    def limbic_couplings(self) -> Sequence[LimbicCoupling]:  # pragma: no cover - simple property
        return self._limbic_couplings

    @property
    def vaginal_structure(self) -> VaginalStructure:  # pragma: no cover - simple property
        return self._vaginal_structure

    # ------------------------------------------------------------------
    # Aggregation helpers
    # ------------------------------------------------------------------
    def build_rig_metadata(self) -> Dict[str, object]:
        """Create rig-friendly metadata dictionaries for the pelvic module."""

        metadata: Dict[str, object] = {
            "module": self.module_name,
            "bones": [asdict(bone) for bone in self._bones],
            "joints": [asdict(joint) for joint in self._joints],
            "muscles": [asdict(muscle) for muscle in self._muscles],
            "nerves": [asdict(nerve) for nerve in self._nerves],
            "visceral_channels": [asdict(channel) for channel in self._visceral_channels],
            "hormones": [asdict(hormone) for hormone in self._hormones],
            "limbic_couplings": [asdict(coupling) for coupling in self._limbic_couplings],
            "vaginal_structure": asdict(self._vaginal_structure),
        }
        self.audit.log_event(
            "build_rig_metadata",
            {
                "bone_count": len(metadata["bones"]),
                "joint_count": len(metadata["joints"]),
                "muscle_count": len(metadata["muscles"]),
                "nerve_count": len(metadata["nerves"]),
                "visceral_channel_count": len(metadata["visceral_channels"]),
                "hormone_count": len(metadata["hormones"]),
                "limbic_coupling_count": len(metadata["limbic_couplings"]),
            },
        )
        return metadata

    def sexual_function_profile(self) -> Dict[str, object]:
        """Summarize arousal support data across muscles, nerves, and hormones."""

        profile: Dict[str, object] = {
            "sensory_paths": {
                nerve.name: {
                    "sensory_targets": nerve.sensory_targets,
                    "sexual_functions": nerve.sexual_functions,
                }
                for nerve in self._nerves
            },
            "muscle_responses": {
                muscle.name: {
                    "primary_function": muscle.primary_function,
                    "sexual_synergy": muscle.sexual_synergy,
                }
                for muscle in self._muscles
            },
            "hormonal_modulation": {
                hormone.name: {
                    "primary_roles": hormone.primary_roles,
                    "sexual_response_phase": hormone.sexual_response_phase,
                }
                for hormone in self._hormones
            },
            "limbic_interlocks": {
                coupling.limbic_structure: coupling.influence
                for coupling in self._limbic_couplings
            },
            "vaginal_structure": {
                "segments": self._vaginal_structure.segments,
                "supportive_tissues": self._vaginal_structure.supportive_tissues,
                "sensory_zones": self._vaginal_structure.sensory_zones,
            },
        }
        self.audit.log_event("sexual_function_profile", {"muscle_count": len(profile["muscle_responses"])})
        return profile


__all__ = ["PelvisModule"]