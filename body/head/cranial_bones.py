"""Simplified cranial bone definitions for rig alignment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple


@dataclass(frozen=True)
class CranialBone:
    """Describes a skull plate or facial bone anchor."""

    name: str
    rig_target: str
    articulates_with: Tuple[str, ...]
    dominant_motion: Tuple[str, ...]
    notes: str = ""


CRANIAL_BONES: tuple[CranialBone, ...] = (
    CranialBone(
        name="frontal_plate",
        rig_target="CTRL_SkullFrontal",
        articulates_with=("parietal_left", "parietal_right", "sphenoid"),
        dominant_motion=("micro_slide", "brow_lift"),
        notes="Supports brow elevation cues tied to affect.face.brow_raise signals.",
    ),
    CranialBone(
        name="parietal_left",
        rig_target="CTRL_SkullParietal_L",
        articulates_with=("parietal_right", "occipital", "temporal_left"),
        dominant_motion=("micro_slide",),
        notes="Provides lateral anchor for ear placement and scalp compression cues.",
    ),
    CranialBone(
        name="parietal_right",
        rig_target="CTRL_SkullParietal_R",
        articulates_with=("parietal_left", "occipital", "temporal_right"),
        dominant_motion=("micro_slide",),
        notes="Mirrors the left parietal plate for symmetrical scalp reactions.",
    ),
    CranialBone(
        name="temporal_left",
        rig_target="CTRL_Temporal_L",
        articulates_with=("sphenoid", "parietal_left"),
        dominant_motion=("jaw_glide_coupling",),
        notes="Carries temporomandibular rotation data without driving the mandible directly.",
    ),
    CranialBone(
        name="temporal_right",
        rig_target="CTRL_Temporal_R",
        articulates_with=("sphenoid", "parietal_right"),
        dominant_motion=("jaw_glide_coupling",),
        notes="Mirrors the left temporal plate for balance in jaw tension cues.",
    ),
    CranialBone(
        name="sphenoid",
        rig_target="CTRL_Sphenoid",
        articulates_with=("temporal_left", "temporal_right", "frontal_plate"),
        dominant_motion=("ocular_platform",),
        notes="Central keystone supporting orbital rig pivots.",
    ),
    CranialBone(
        name="zygomatic_arch_left",
        rig_target="CTRL_Zygomatic_L",
        articulates_with=("temporal_left", "maxilla"),
        dominant_motion=("smile_support",),
        notes="Provides cheek lift reaction when zygomaticus major fires.",
    ),
    CranialBone(
        name="zygomatic_arch_right",
        rig_target="CTRL_Zygomatic_R",
        articulates_with=("temporal_right", "maxilla"),
        dominant_motion=("smile_support",),
        notes="Balances cheek elevation on the right side.",
    ),
    CranialBone(
        name="maxilla",
        rig_target="CTRL_Maxilla",
        articulates_with=("zygomatic_arch_left", "zygomatic_arch_right", "nasal"),
        dominant_motion=("upper_lip_support",),
        notes="Anchors nasal and philtrum movement for lip raise expressions.",
    ),
    CranialBone(
        name="mandible",
        rig_target="CTRL_Mandible",
        articulates_with=("temporal_left", "temporal_right"),
        dominant_motion=("jaw_rotation", "jaw_translation"),
        notes="Included for completeness but constrained to stay within cranial bounds.",
    ),
    CranialBone(
        name="occipital",
        rig_target="CTRL_Occipital",
        articulates_with=("parietal_left", "parietal_right", "temporal_left", "temporal_right"),
        dominant_motion=("micro_slide",),
        notes="Head pose root used to blend with neck module without crossing into cervical spine.",
    ),
)


def iter_cranial_bones() -> Iterable[CranialBone]:
    """Iterate configured cranial bones."""

    return iter(CRANIAL_BONES)


__all__ = ["CranialBone", "CRANIAL_BONES", "iter_cranial_bones"]