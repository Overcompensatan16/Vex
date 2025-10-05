"""Core torso routing module aggregating musculoskeletal metadata."""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Sequence

from audit.audit_logger_factory import AuditLoggerFactory

from .bones import TORSO_BONES, TorsoBone
from .ligaments import TORSO_LIGAMENTS, TorsoLigament
from .muscles import TORSO_MUSCLES, TorsoMuscle
from .skin import TORSO_SKIN_REGIONS, TorsoSkinRegion


class TorsoModule:
    """Aggregate torso musculoskeletal structures for rig export."""

    module_name = "torso"

    def __init__(self, *, audit_factory: AuditLoggerFactory | None = None) -> None:
        self.audit = audit_factory or AuditLoggerFactory(self.module_name)
        self._bones: Sequence[TorsoBone] = tuple(TORSO_BONES)
        self._ligaments: Sequence[TorsoLigament] = tuple(TORSO_LIGAMENTS)
        self._muscles: Sequence[TorsoMuscle] = tuple(TORSO_MUSCLES)
        self._skin_regions: Sequence[TorsoSkinRegion] = tuple(TORSO_SKIN_REGIONS)
        self.audit.log_event(
            "init",
            {
                "module": self.module_name,
                "bone_count": len(self._bones),
                "ligament_count": len(self._ligaments),
                "muscle_count": len(self._muscles),
                "skin_region_count": len(self._skin_regions),
            },
        )

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------
    @property
    def bones(self) -> Sequence[TorsoBone]:  # pragma: no cover - simple property
        return self._bones

    @property
    def ligaments(self) -> Sequence[TorsoLigament]:  # pragma: no cover - simple property
        return self._ligaments

    @property
    def muscles(self) -> Sequence[TorsoMuscle]:  # pragma: no cover - simple property
        return self._muscles

    @property
    def skin_regions(self) -> Sequence[TorsoSkinRegion]:  # pragma: no cover - simple property
        return self._skin_regions

    # ------------------------------------------------------------------
    # Aggregation helpers
    # ------------------------------------------------------------------
    def log_structure_summary(self) -> None:
        """Log a human-friendly description of the torso assembly."""

        self.audit.log_event(
            "structure_summary",
            {
                "bones": [bone.name for bone in self._bones],
                "ligaments": [ligament.name for ligament in self._ligaments],
                "muscles": [muscle.name for muscle in self._muscles],
                "skin_regions": [region.name for region in self._skin_regions],
            },
        )

    def build_rig_metadata(self) -> Dict[str, object]:
        """Create metadata dictionaries for downstream rig integration."""

        metadata: Dict[str, object] = {
            "module": self.module_name,
            "bones": [asdict(bone) for bone in self._bones],
            "ligaments": [asdict(ligament) for ligament in self._ligaments],
            "muscles": [asdict(muscle) for muscle in self._muscles],
            "skin_regions": [asdict(region) for region in self._skin_regions],
        }
        self.audit.log_event(
            "build_rig_metadata",
            {
                "bone_count": len(metadata["bones"]),
                "ligament_count": len(metadata["ligaments"]),
                "muscle_count": len(metadata["muscles"]),
                "skin_region_count": len(metadata["skin_regions"]),
            },
        )
        return metadata


__all__ = ["TorsoModule"]