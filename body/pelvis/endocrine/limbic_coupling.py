"""Mappings between limbic structures and pelvic endocrine modulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class LimbicCoupling:
    """Limbic feedback loop coupling emotional state to pelvic responses."""

    limbic_structure: str
    hormone: str
    influence: str
    behavioral_output: str


LIMBIC_COUPLINGS: Tuple[LimbicCoupling, ...] = (
    LimbicCoupling(
        limbic_structure="Amygdala",
        hormone="Oxytocin",
        influence="Dampens threat vigilance to permit intimate proximity",
        behavioral_output="Encourages sustained eye contact and relaxed posture",
    ),
    LimbicCoupling(
        limbic_structure="Hippocampus",
        hormone="Estrogen",
        influence="Enhances contextual memory of positive sexual experiences",
        behavioral_output="Promotes anticipatory desire via recalled cues",
    ),
    LimbicCoupling(
        limbic_structure="Nucleus accumbens",
        hormone="Testosterone",
        influence="Amplifies reward sensitivity for erotic stimuli",
        behavioral_output="Drives approach behavior and exploratory touch",
    ),
    LimbicCoupling(
        limbic_structure="Insula",
        hormone="Relaxin",
        influence="Integrates interoceptive signals of pelvic openness",
        behavioral_output="Facilitates slow breathing and pelvic floor release",
    ),
)


__all__ = ["LimbicCoupling", "LIMBIC_COUPLINGS"]