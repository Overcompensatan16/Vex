"""Torso musculature metadata definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass(frozen=True)
class TorsoMuscle:
    """Aggregated muscle group driving torso motion."""

    name: str
    actuators: Tuple[str, ...]
    primary_function: str
    fiber_type: str
    notes: str = ""


TORSO_MUSCLES: List[TorsoMuscle] = [
    TorsoMuscle(
        name="rectus_abdominis",
        actuators=("CTRL_LumbarSpine", "CTRL_Pelvis"),
        primary_function="Spinal flexion and abdominal compression",
        fiber_type="mixed",
        notes="Blends with breathing curves to articulate abdominal wall.",
    ),
    TorsoMuscle(
        name="erector_spinae",
        actuators=("CTRL_ThoracicSpine", "CTRL_LumbarSpine"),
        primary_function="Spinal extension and posture control",
        fiber_type="slow",
        notes="Feeds posture stabilization metadata during locomotion.",
    ),
    TorsoMuscle(
        name="obliques_internal_external",
        actuators=("CTRL_ThoracicSpine", "CTRL_Pelvis"),
        primary_function="Axial rotation and lateral flexion",
        fiber_type="mixed",
        notes="Coordinates counter-rotation with arm swing phases.",
    ),
    TorsoMuscle(
        name="transversus_abdominis",
        actuators=("CTRL_LumbarSpine",),
        primary_function="Core stabilization and intra-abdominal pressure",
        fiber_type="slow",
        notes="Acts as feed-forward brace for reflexive balance reactions.",
    ),
    TorsoMuscle(
        name="quadratus_lumborum",
        actuators=("CTRL_LumbarSpine", "CTRL_Pelvis"),
        primary_function="Pelvic hiking and lumbar lateral flexion",
        fiber_type="fast",
        notes="Supplies gait-driven pelvic drop compensation.",
    ),
]


def iter_torso_muscles() -> Iterable[TorsoMuscle]:
    """Iterate over configured torso muscles."""

    return iter(TORSO_MUSCLES)


__all__ = ["TorsoMuscle", "TORSO_MUSCLES", "iter_torso_muscles"]