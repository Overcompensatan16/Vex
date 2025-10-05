"""Pelvic floor muscle definitions with continence and sexual synergy roles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class PelvicFloorMuscle:
    """Representation of a pelvic floor muscle and its coordinated actions."""

    name: str
    layer: str
    primary_function: str
    associated_organs: Tuple[str, ...]
    sexual_synergy: Tuple[str, ...]


PELVIC_FLOOR_MUSCLES: Tuple[PelvicFloorMuscle, ...] = (
    PelvicFloorMuscle(
        name="Pubococcygeus",
        layer="Levator ani",
        primary_function="Supports pelvic viscera and maintains continence",
        associated_organs=("Urethra", "Vagina", "Rectum"),
        sexual_synergy=(
            "Provides rhythmic contractions during orgasm",
            "Maintains vaginal tone for proprioceptive feedback",
        ),
    ),
    PelvicFloorMuscle(
        name="Iliococcygeus",
        layer="Levator ani",
        primary_function="Elevates pelvic floor and stabilizes coccyx",
        associated_organs=("Vagina", "Anal canal"),
        sexual_synergy=(
            "Supports vaginal lengthening during arousal",
            "Assists in recoil after pelvic thrust cycles",
        ),
    ),
    PelvicFloorMuscle(
        name="Puborectalis",
        layer="Levator ani",
        primary_function="Maintains anorectal angle for continence",
        associated_organs=("Rectum", "Vagina"),
        sexual_synergy=(
            "Coordinates with deep pelvic fascia for pleasurable tension",
            "Stabilizes perineal body enhancing orgasmic wave propagation",
        ),
    ),
    PelvicFloorMuscle(
        name="Bulbospongiosus",
        layer="Superficial perineal",
        primary_function="Compresses vestibular bulbs and assists clitoral erection",
        associated_organs=("Vestibular bulbs", "Clitoris", "Vaginal introitus"),
        sexual_synergy=(
            "Facilitates clitoral engorgement",
            "Rhythmic contractions increase orgasmic intensity",
        ),
    ),
    PelvicFloorMuscle(
        name="Ischiocavernosus",
        layer="Superficial perineal",
        primary_function="Maintains blood within clitoral crura",
        associated_organs=("Clitoral crura", "Ischial ramus"),
        sexual_synergy=(
            "Amplifies tactile sensitivity along anterior vaginal wall",
            "Stabilizes pelvic outlet for partner alignment",
        ),
    ),
)


def build_muscle_support_map() -> Dict[str, Tuple[str, ...]]:
    """Return a map of muscles to the organs they support."""

    return {muscle.name: muscle.associated_organs for muscle in PELVIC_FLOOR_MUSCLES}


__all__ = ["PelvicFloorMuscle", "PELVIC_FLOOR_MUSCLES", "build_muscle_support_map"]