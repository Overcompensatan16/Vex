"""Sensory nerve definitions for the pelvis with reflex and sexual pathways."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class PelvicNerve:
    """Description of a pelvic nerve including sensory reach and reflex arcs."""

    name: str
    origin_segments: Tuple[str, ...]
    sensory_targets: Tuple[str, ...]
    reflex_arcs: Tuple[str, ...]
    sexual_functions: Tuple[str, ...]


PELVIC_NERVES: Tuple[PelvicNerve, ...] = (
    PelvicNerve(
        name="Pudendal nerve",
        origin_segments=("S2", "S3", "S4"),
        sensory_targets=(
            "Clitoris",
            "Vulvar vestibule",
            "Perineal skin",
            "Posterior vaginal wall",
        ),
        reflex_arcs=("Anal wink reflex", "Bulbocavernosus reflex"),
        sexual_functions=(
            "Transmits high-resolution touch from clitoral complex",
            "Mediates orgasmic motor response via bulbospongiosus",
        ),
    ),
    PelvicNerve(
        name="Pelvic splanchnic nerves",
        origin_segments=("S2", "S3", "S4"),
        sensory_targets=("Cervix", "Uterus", "Bladder trigone", "Anterior vaginal wall"),
        reflex_arcs=("Detrusor activation", "Cervical relaxation"),
        sexual_functions=(
            "Initiates vasodilation for genital engorgement",
            "Coordinates uterine contractions during orgasm",
        ),
    ),
    PelvicNerve(
        name="Ilioinguinal nerve",
        origin_segments=("L1",),
        sensory_targets=("Mons pubis", "Labia majora"),
        reflex_arcs=("Cremasteric analog modulation",),
        sexual_functions=(
            "Enhances arousal by conveying tactile warmth at mons",
            "Supports protective withdrawal reflex when overstimulated",
        ),
    ),
    PelvicNerve(
        name="Hypogastric nerve",
        origin_segments=("T12", "L1", "L2"),
        sensory_targets=("Cervix", "Upper vagina", "Bladder dome"),
        reflex_arcs=("Sympathetic guarding reflex",),
        sexual_functions=(
            "Conveys sympathetic arousal signals during plateau phase",
            "Coordinates orgasmic emission with pelvic floor rebound",
        ),
    ),
)


def map_reflex_paths() -> Dict[str, Tuple[str, ...]]:
    """Return mapping of nerve names to their reflex arcs."""

    return {nerve.name: nerve.reflex_arcs for nerve in PELVIC_NERVES}


__all__ = ["PelvicNerve", "PELVIC_NERVES", "map_reflex_paths"]