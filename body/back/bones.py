"""Back skeletal segment metadata supporting movement and stability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass(frozen=True)
class BackBone:
    """Simplified spinal segment for rig export and posture control."""

    name: str
    rig_target: str
    segment: str
    length_cm: float
    parent: str | None = None
    degrees_of_freedom: Tuple[str, ...] = ()
    notes: str = ""


BACK_BONES: List[BackBone] = [
    BackBone(
        name="cervicothoracic_junction",
        rig_target="CTRL_BackCervicothoracic",
        segment="C7-T2",
        length_cm=6.5,
        parent=None,
        degrees_of_freedom=("flex", "extend", "rotate"),
        notes="Transitions head posture adjustments into thoracic control curves.",
    ),
    BackBone(
        name="upper_thoracic_unit",
        rig_target="CTRL_BackThoracicUpper",
        segment="T1-T6",
        length_cm=17.8,
        parent="cervicothoracic_junction",
        degrees_of_freedom=("flex", "extend", "rotate", "sidebend"),
        notes="Carries counter-rotation data for shoulder girdle coupling.",
    ),
    BackBone(
        name="lower_thoracic_unit",
        rig_target="CTRL_BackThoracicLower",
        segment="T7-T12",
        length_cm=16.2,
        parent="upper_thoracic_unit",
        degrees_of_freedom=("flex", "extend", "rotate", "sidebend"),
        notes="Feeds rib glide compensation into lumbar blendshapes.",
    ),
    BackBone(
        name="lumbar_unit",
        rig_target="CTRL_BackLumbar",
        segment="L1-L5",
        length_cm=19.5,
        parent="lower_thoracic_unit",
        degrees_of_freedom=("flex", "extend", "sidebend"),
        notes="Primary driver for gait-induced pelvic translations and bracing.",
    ),
    BackBone(
        name="sacral_base",
        rig_target="CTRL_BackSacrum",
        segment="S1-S2",
        length_cm=9.2,
        parent="lumbar_unit",
        degrees_of_freedom=("tilt", "yaw"),
        notes="Anchors pelvic motion and distributes ground reaction adjustments.",
    ),
]


def iter_back_bones() -> Iterable[BackBone]:
    """Iterate over configured back bones."""

    return iter(BACK_BONES)


__all__ = ["BackBone", "BACK_BONES", "iter_back_bones"]