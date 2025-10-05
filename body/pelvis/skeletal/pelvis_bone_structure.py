"""Data definitions for pelvic bones and vaginal support structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class PelvicBone:
    """Representation of a pelvic bone and its articulations."""

    name: str
    articulations: Tuple[str, ...]
    functions: Tuple[str, ...]
    sexual_health_roles: Tuple[str, ...]


@dataclass(frozen=True)
class VaginalStructure:
    """Layered view of the vaginal canal and its supportive tissues."""

    segments: Tuple[str, ...]
    supportive_tissues: Tuple[str, ...]
    sensory_zones: Tuple[str, ...]
    lubrication_support: Tuple[str, ...]


PELVIC_BONES: Tuple[PelvicBone, ...] = (
    PelvicBone(
        name="Ilium",
        articulations=("Sacrum", "Femur via acetabulum"),
        functions=(
            "Supports abdominal organs",
            "Forms superior pelvis",
            "Provides attachment for gluteal musculature",
        ),
        sexual_health_roles=(
            "Stabilizes pelvic inlet during arousal",
            "Transfers load from torso during partnered movement",
        ),
    ),
    PelvicBone(
        name="Ischium",
        articulations=("Pubis", "Femur via acetabulum"),
        functions=(
            "Forms posteroinferior pelvis",
            "Supports body weight while seated",
            "Anchors hamstrings and pelvic floor",
        ),
        sexual_health_roles=(
            "Provides leverage for pelvic floor contractions",
            "Protects pudendal nerve pathways",
        ),
    ),
    PelvicBone(
        name="Pubis",
        articulations=("Ischium", "Pubic symphysis"),
        functions=(
            "Forms anterior pelvic ring",
            "Stabilizes hip joint via acetabulum",
            "Supports urogenital diaphragm",
        ),
        sexual_health_roles=(
            "Shields clitoral crura and vestibular bulbs",
            "Maintains spacing for vaginal canal expansion",
        ),
    ),
    PelvicBone(
        name="Sacrum",
        articulations=("L5 vertebra", "Ilium"),
        functions=(
            "Transmits spinal load into pelvis",
            "Forms posterior pelvic wall",
            "Creates neural passage for pelvic nerves",
        ),
        sexual_health_roles=(
            "Protects sacral plexus involved in orgasmic signaling",
            "Coordinates with coccyx for pelvic floor recoil",
        ),
    ),
    PelvicBone(
        name="Coccyx",
        articulations=("Sacrum",),
        functions=(
            "Provides attachment for pelvic floor",
            "Supports ligamentous anchoring",
            "Assists in balance when seated",
        ),
        sexual_health_roles=(
            "Acts as hinge for orgasmic rhythmic motion",
            "Supports posterior vaginal wall tone",
        ),
    ),
)


VAGINAL_STRUCTURE = VaginalStructure(
    segments=(
        "Vestibule with clitoral complex",
        "Mid-vaginal canal with rugae",
        "Posterior fornix wrapping cervix",
    ),
    supportive_tissues=(
        "Pubocervical fascia",
        "Perineal body",
        "Levator ani muscular sling",
    ),
    sensory_zones=(
        "Clitoral bulbs and vestibular mucosa",
        "Anterior wall with urethral sponge",
        "Posterior fornix with deep pressure receptors",
    ),
    lubrication_support=(
        "Bartholin glands providing mucous release",
        "Vascular engorgement enhancing transudate",
    ),
)


__all__ = ["PelvicBone", "VaginalStructure", "PELVIC_BONES", "VAGINAL_STRUCTURE"]