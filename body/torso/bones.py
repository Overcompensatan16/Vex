"""Torso skeletal metadata definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class TorsoBone:
    """Simplified torso bone representation for rig export."""

    name: str
    rig_target: str
    length_cm: float
    parent: str | None = None
    degrees_of_freedom: tuple[str, ...] = ()
    notes: str = ""


TORSO_BONES: List[TorsoBone] = [
    TorsoBone(
        name="cranial_base",
        rig_target="CTRL_CranialBase",
        length_cm=12.5,
        parent=None,
        degrees_of_freedom=("tilt", "yaw", "nod"),
        notes="Provides head sway integration for cervical spine coupling.",
    ),
    TorsoBone(
        name="cervical_spine",
        rig_target="CTRL_CervicalSpine",
        length_cm=13.0,
        parent="cranial_base",
        degrees_of_freedom=("flex", "rotate", "sidebend"),
        notes="Aggregated cervical stack for head posture blending.",
    ),
    TorsoBone(
        name="thoracic_spine",
        rig_target="CTRL_ThoracicSpine",
        length_cm=30.0,
        parent="cervical_spine",
        degrees_of_freedom=("flex", "rotate", "sidebend"),
        notes="Carries breathing and shoulder girdle counter-rotation curves.",
    ),
    TorsoBone(
        name="lumbar_spine",
        rig_target="CTRL_LumbarSpine",
        length_cm=26.0,
        parent="thoracic_spine",
        degrees_of_freedom=("flex", "rotate", "sidebend"),
        notes="Routes core stabilization metadata for gait transfer.",
    ),
    TorsoBone(
        name="sacrum",
        rig_target="CTRL_Sacrum",
        length_cm=10.0,
        parent="lumbar_spine",
        degrees_of_freedom=("tilt", "yaw"),
        notes="Anchors pelvic motion blending and ground reaction offsets.",
    ),
    TorsoBone(
        name="pelvis",
        rig_target="CTRL_Pelvis",
        length_cm=28.0,
        parent="sacrum",
        degrees_of_freedom=("tilt", "yaw", "shift"),
        notes="Primary pelvis control distributing leg forces into spine.",
    ),
    TorsoBone(
        name="sternum",
        rig_target="CTRL_Sternum",
        length_cm=17.0,
        parent="thoracic_spine",
        degrees_of_freedom=("elevate", "twist"),
        notes="Handles rib expansion and clavicle anchoring offsets.",
    ),
]


def iter_torso_bones() -> Iterable[TorsoBone]:
    """Iterate over configured torso bones."""

    return iter(TORSO_BONES)


__all__ = ["TorsoBone", "TORSO_BONES", "iter_torso_bones"]