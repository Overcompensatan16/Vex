"""Torso ligament metadata definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass(frozen=True)
class TorsoLigament:
    """Describes ligament support structures in the torso."""

    name: str
    attachments: Tuple[str, str]
    stiffness: float
    function: str
    notes: str = ""


TORSO_LIGAMENTS: List[TorsoLigament] = [
    TorsoLigament(
        name="anterior_longitudinal_ligament",
        attachments=("cervical_spine", "sacrum"),
        stiffness=0.82,
        function="Limits hyperextension across vertebral bodies.",
        notes="Sample stiffness normalized for rig spring interpretation.",
    ),
    TorsoLigament(
        name="posterior_longitudinal_ligament",
        attachments=("cervical_spine", "lumbar_spine"),
        stiffness=0.74,
        function="Maintains vertebral alignment and dampens flexion.",
        notes="Feeds spine oscillation damping for idle breathing.",
    ),
    TorsoLigament(
        name="ligamentum_flavum",
        attachments=("thoracic_spine", "lumbar_spine"),
        stiffness=0.65,
        function="Supports elastic recoil during controlled extension.",
    ),
    TorsoLigament(
        name="iliolumbar_ligament",
        attachments=("lumbar_spine", "pelvis"),
        stiffness=0.88,
        function="Stabilizes transition between lumbar spine and pelvis.",
        notes="Critical for transferring leg reaction forces into core.",
    ),
]


def iter_torso_ligaments() -> Iterable[TorsoLigament]:
    """Iterate over configured torso ligaments."""

    return iter(TORSO_LIGAMENTS)


__all__ = ["TorsoLigament", "TORSO_LIGAMENTS", "iter_torso_ligaments"]