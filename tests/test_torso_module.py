"""Tests for the torso musculoskeletal aggregation module."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from audit.audit_logger_factory import AuditLoggerFactory
from body.torso import (
    TORSO_BONES,
    TORSO_LIGAMENTS,
    TORSO_MUSCLES,
    TORSO_SKIN_REGIONS,
    TorsoModule,
)


def test_torso_module_metadata_roundtrip(tmp_path) -> None:
    audit_factory = AuditLoggerFactory(
        "torso_test",
        log_path=str(tmp_path / "torso_audit.jsonl"),
    )
    module = TorsoModule(audit_factory=audit_factory)
    module.log_structure_summary()
    metadata = module.build_rig_metadata()

    assert metadata["module"] == "torso"
    assert len(metadata["bones"]) == len(TORSO_BONES)
    assert len(metadata["ligaments"]) == len(TORSO_LIGAMENTS)
    assert len(metadata["muscles"]) == len(TORSO_MUSCLES)
    assert len(metadata["skin_regions"]) == len(TORSO_SKIN_REGIONS)

    # Verify that dataclass conversion preserved key structure.
    for bone_dict, bone in zip(metadata["bones"], TORSO_BONES, strict=True):
        assert bone_dict["name"] == bone.name
        assert bone_dict["rig_target"] == bone.rig_target

    for ligament_dict, ligament in zip(metadata["ligaments"], TORSO_LIGAMENTS, strict=True):
        assert tuple(ligament_dict["attachments"]) == tuple(ligament.attachments)

    for skin_dict in metadata["skin_regions"]:
        assert "surface_area_cm2" in skin_dict
        assert skin_dict["surface_area_cm2"] > 0