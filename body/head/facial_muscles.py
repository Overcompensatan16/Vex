"""Facial muscle metadata tuned for expression routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple


@dataclass(frozen=True)
class FacialMuscle:
    """Represents a facial muscle influencing blendshapes."""

    name: str
    rig_target: str
    primary_action: str
    supported_expressions: Tuple[str, ...]
    notes: str = ""


FACIAL_MUSCLES: tuple[FacialMuscle, ...] = (
    FacialMuscle(
        name="frontalis",
        rig_target="CTRL_BrowLift",
        primary_action="elevates eyebrows",
        supported_expressions=("surprise", "curiosity"),
        notes="Pairs with affect.face.brow_raise signals for open-eyed affect.",
    ),
    FacialMuscle(
        name="orbicularis_oculi",
        rig_target="CTRL_EyelidClose",
        primary_action="closes eyelids",
        supported_expressions=("blink", "smile_soft", "focus"),
        notes="Used for blink reflex and soft smiling squint variations.",
    ),
    FacialMuscle(
        name="zygomaticus_major",
        rig_target="CTRL_CheekRaise",
        primary_action="pulls mouth corners upward",
        supported_expressions=("smile", "delight"),
        notes="Primary smile driver encouraging asymmetry via per-side tuning.",
    ),
    FacialMuscle(
        name="levator_labii_superioris",
        rig_target="CTRL_UpperLipRaise",
        primary_action="elevates upper lip",
        supported_expressions=("snarl", "disgust", "smile"),
        notes="Allows nose wrinkle coupling when disgust intensity rises.",
    ),
    FacialMuscle(
        name="depressor_anguli_oris",
        rig_target="CTRL_MouthFrown",
        primary_action="pulls mouth corners downward",
        supported_expressions=("frown", "sadness"),
        notes="Enables quick affect transitions between pout and deep frown.",
    ),
    FacialMuscle(
        name="mentalis",
        rig_target="CTRL_ChinRaise",
        primary_action="pushes chin upward",
        supported_expressions=("doubt", "pout"),
        notes="Adds tension to lower lip for pouty or uncertain emotions.",
    ),
    FacialMuscle(
        name="buccinator",
        rig_target="CTRL_CheekCompress",
        primary_action="compresses cheeks",
        supported_expressions=("focus", "cheek_suck"),
        notes="Useful for phoneme support and cheek-suck idle variations.",
    ),
)


def iter_facial_muscles() -> Iterable[FacialMuscle]:
    """Iterate configured facial muscles."""

    return iter(FACIAL_MUSCLES)


__all__ = ["FacialMuscle", "FACIAL_MUSCLES", "iter_facial_muscles"]