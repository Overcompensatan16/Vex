from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple


@dataclass(frozen=True)
class FacialExpression:
    """Named expression linking muscles to registry signal paths."""

    name: str
    description: str
    primary_muscles: Tuple[str, ...]
    signal_path: str
    default_intensity: float = 0.0


FACIAL_EXPRESSIONS: tuple[FacialExpression, ...] = (
    FacialExpression(
        name="soft_smile",
        description="Gentle bilateral smile used for approachable idle states.",
        primary_muscles=("zygomaticus_major", "orbicularis_oculi"),
        signal_path="affect.face.smile",
        default_intensity=0.35,
    ),
    FacialExpression(
        name="brow_raise",
        description="Lifted brows widening the eyes for curiosity or surprise.",
        primary_muscles=("frontalis",),
        signal_path="affect.face.brow_raise",
        default_intensity=0.4,
    ),
    FacialExpression(
        name="focused_squint",
        description="Partial lid closure encouraging attentive focus.",
        primary_muscles=("orbicularis_oculi",),
        signal_path="affect.face.squint",
        default_intensity=0.25,
    ),
    FacialExpression(
        name="disgust_wrinkle",
        description="Upper lip raise with nose wrinkle for aversive reactions.",
        primary_muscles=("levator_labii_superioris",),
        signal_path="affect.face.nose_wrinkle",
        default_intensity=0.45,
    ),
    FacialExpression(
        name="pout",
        description="Lower lip protrusion conveying doubt or pleading.",
        primary_muscles=("mentalis",),
        signal_path="affect.face.pout",
        default_intensity=0.3,
    ),
)


def iter_facial_expressions() -> Iterable[FacialExpression]:
    """Iterate configured facial expressions."""

    return iter(FACIAL_EXPRESSIONS)


__all__ = ["FacialExpression", "FACIAL_EXPRESSIONS", "iter_facial_expressions"]