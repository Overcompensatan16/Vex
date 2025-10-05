"""Reproductive hormone profiles driving pelvic and sexual function."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ReproductiveHormone:
    """Hormone with sources, roles, and sexual response phase mapping."""

    name: str
    primary_sources: Tuple[str, ...]
    primary_roles: Tuple[str, ...]
    sexual_response_phase: str


REPRODUCTIVE_HORMONES: Tuple[ReproductiveHormone, ...] = (
    ReproductiveHormone(
        name="Estrogen",
        primary_sources=("Ovarian follicles", "Adipose tissue"),
        primary_roles=(
            "Maintains vaginal epithelium and lubrication",
            "Supports pelvic floor collagen synthesis",
            "Enhances sensitivity of pudendal afferents",
        ),
        sexual_response_phase="Desire/plateau",
    ),
    ReproductiveHormone(
        name="Progesterone",
        primary_sources=("Corpus luteum", "Adrenal cortex"),
        primary_roles=(
            "Stabilizes endometrium",
            "Modulates smooth muscle tone of uterus",
            "Dampens sympathetic overactivity",
        ),
        sexual_response_phase="Plateau",
    ),
    ReproductiveHormone(
        name="Oxytocin",
        primary_sources=("Posterior pituitary",),
        primary_roles=(
            "Triggers orgasmic uterine contractions",
            "Promotes pair bonding and affectionate behavior",
            "Enhances trust signals from limbic system",
        ),
        sexual_response_phase="Orgasm",
    ),
    ReproductiveHormone(
        name="Relaxin",
        primary_sources=("Corpus luteum", "Placenta"),
        primary_roles=(
            "Softens connective tissue at pubic symphysis",
            "Increases pelvic joint flexibility",
            "Facilitates vaginal expansion",
        ),
        sexual_response_phase="Arousal",
    ),
    ReproductiveHormone(
        name="Testosterone",
        primary_sources=("Ovaries", "Adrenal glands"),
        primary_roles=(
            "Boosts libido",
            "Supports clitoral engorgement",
            "Maintains muscle tone in pelvic floor",
        ),
        sexual_response_phase="Desire",
    ),
)


def hormone_profile_map() -> Tuple[Tuple[str, str], ...]:
    """Return simplified mapping of hormone names to response phases."""

    return tuple((hormone.name, hormone.sexual_response_phase) for hormone in REPRODUCTIVE_HORMONES)


__all__ = ["ReproductiveHormone", "REPRODUCTIVE_HORMONES", "hormone_profile_map"]