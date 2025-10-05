"""Back muscle group definitions prioritizing movement and stability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass(frozen=True)
class BackMuscle:
    """Aggregated muscle bundle responsible for spinal control."""

    name: str
    actuators: Tuple[str, ...]
    primary_actions: Tuple[str, ...]
    stability_role: str
    fiber_profile: str
    notes: str = ""


BACK_MUSCLES: List[BackMuscle] = [
    BackMuscle(
        name="erector_spinae_longissimus",
        actuators=("CTRL_BackThoracicUpper", "CTRL_BackThoracicLower", "CTRL_BackLumbar"),
        primary_actions=("extension", "anti_gravity support"),
        stability_role="Maintains upright posture and delivers baseline spinal stability.",
        fiber_profile="slow_dominant",
        notes="Feeds tonic extension curves into righting reflex metadata.",
    ),
    BackMuscle(
        name="multifidus",
        actuators=("CTRL_BackLumbar", "CTRL_BackSacrum"),
        primary_actions=("segmental_stabilization", "fine_tuning"),
        stability_role="Provides vertebra-to-vertebra stiffness and shear stability.",
        fiber_profile="mixed",
        notes="Outputs stiffness envelopes responding to vestibular perturbations.",
    ),
    BackMuscle(
        name="quadratus_lumborum_posterior",
        actuators=("CTRL_BackLumbar", "CTRL_BackSacrum"),
        primary_actions=("lateral_flexion", "pelvic_control"),
        stability_role="Balances pelvic hike with contralateral leg swing for frontal stability.",
        fiber_profile="fast_mixed",
        notes="Coordinates with hip abductors for frontal plane stability.",
    ),
    BackMuscle(
        name="thoracolumbar_fascia_cinch",
        actuators=("CTRL_BackThoracicLower", "CTRL_BackLumbar"),
        primary_actions=("force_coupling", "tension_distribution"),
        stability_role="Ties latissimus and gluteal drive into lumbar stability support.",
        fiber_profile="aponeurotic",
        notes="Models sheet tension contributing to whole-body bracing.",
    ),
    BackMuscle(
        name="semispinalis_cervicis",
        actuators=("CTRL_BackCervicothoracic", "CTRL_BackThoracicUpper"),
        primary_actions=("extension", "rotation_control"),
        stability_role="Stabilizes cervicothoracic junction to protect head motion stability.",
        fiber_profile="mixed",
        notes="Ensures smooth energy transfer between head sway and spine.",
    ),
]


def iter_back_muscles() -> Iterable[BackMuscle]:
    """Iterate over configured back muscles."""

    return iter(BACK_MUSCLES)


__all__ = ["BackMuscle", "BACK_MUSCLES", "iter_back_muscles"]