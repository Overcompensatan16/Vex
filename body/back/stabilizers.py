"""Passive stabilizing structures for the back module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass(frozen=True)
class BackStabilizer:
    """Structure providing passive stability and proprioceptive feedback."""

    name: str
    attachments: Tuple[str, str]
    stiffness: float
    damping: float
    role: str
    feedback_channels: Tuple[str, ...] = ()
    notes: str = ""


BACK_STABILIZERS: List[BackStabilizer] = [
    BackStabilizer(
        name="thoracolumbar_fascia",
        attachments=("lower_thoracic_unit", "lumbar_unit"),
        stiffness=0.78,
        damping=0.42,
        role="Spreads load between thoracic and pelvic segments during lift/brace.",
        feedback_channels=("proprioceptive.thoracolumbar", "cutaneous.lower_back"),
        notes="Acts as tension bridge for latissimus and gluteal coupling.",
    ),
    BackStabilizer(
        name="interspinous_ligaments",
        attachments=("upper_thoracic_unit", "lower_thoracic_unit"),
        stiffness=0.71,
        damping=0.36,
        role="Restrains flexion and enhances segmental positional awareness.",
        feedback_channels=("proprioceptive.spinal_joint",),
        notes="Supports micro-adjustments when balancing on unstable surfaces.",
    ),
    BackStabilizer(
        name="supraspinous_ligament",
        attachments=("cervicothoracic_junction", "lumbar_unit"),
        stiffness=0.69,
        damping=0.31,
        role="Maintains posterior tension band continuity across spine.",
        feedback_channels=("proprioceptive.posterior_column",),
        notes="Feeds into righting reflexes for rapid lean recovery.",
    ),
    BackStabilizer(
        name="iliolumbar_complex",
        attachments=("lumbar_unit", "sacral_base"),
        stiffness=0.87,
        damping=0.48,
        role="Stabilizes lumbosacral junction against shear from leg drive.",
        feedback_channels=("vestibular.integration", "proprioceptive.sacroiliac"),
        notes="Critical when translating ground reaction forces into spine.",
    ),
]


def iter_back_stabilizers() -> Iterable[BackStabilizer]:
    """Iterate over configured stabilizers."""

    return iter(BACK_STABILIZERS)


__all__ = ["BackStabilizer", "BACK_STABILIZERS", "iter_back_stabilizers"]