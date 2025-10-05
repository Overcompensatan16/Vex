"""Visceral feedback channels describing pelvic comfort and tension states."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class VisceralSignal:
    """Internal signal representing visceral tone, comfort, and stretch."""

    organ: str
    receptors: Tuple[str, ...]
    comfort_states: Tuple[str, ...]
    sexual_modulation: Tuple[str, ...]


VISCERAL_FEEDBACK_CHANNELS: Tuple[VisceralSignal, ...] = (
    VisceralSignal(
        organ="Bladder",
        receptors=("Stretch receptors", "Chemoreceptors"),
        comfort_states=(
            "Baseline fullness",
            "Urgency when overstretched",
            "Relaxed detrusor during parasympathetic activation",
        ),
        sexual_modulation=(
            "Pelvic splanchnic activation relaxes detrusor for arousal",
            "Guarding reflex via hypogastric nerve prevents leakage",
        ),
    ),
    VisceralSignal(
        organ="Uterus",
        receptors=("Mechanoreceptors", "Prostaglandin-sensitive cells"),
        comfort_states=(
            "Neutral tone",
            "Menstrual cramping",
            "Post-orgasmic afterglow contractions",
        ),
        sexual_modulation=(
            "Oxytocin surges increase rhythmic contractions",
            "Parasympathetic input softens cervical os for pleasure",
        ),
    ),
    VisceralSignal(
        organ="Vagina",
        receptors=("Ruffini endings", "Free nerve endings", "Baroreceptors"),
        comfort_states=(
            "Resting mucosal rugae",
            "Lubricated expansion",
            "Overstretch discomfort",
        ),
        sexual_modulation=(
            "Engorgement increases mucosal transudate",
            "Pudendal afferents refine pressure and temperature mapping",
        ),
    ),
    VisceralSignal(
        organ="Rectum",
        receptors=("Stretch receptors", "Chemosensitive cells"),
        comfort_states=(
            "Empty resting state",
            "Filling awareness",
            "Urgency contraction",
        ),
        sexual_modulation=(
            "Levator ani tension shields vaginal posterior wall",
            "Sympathetic activation suppresses rectal motility during arousal",
        ),
    ),
)


def baseline_comfort_map() -> Dict[str, Tuple[str, ...]]:
    """Return mapping of organs to their baseline comfort states."""

    return {signal.organ: signal.comfort_states for signal in VISCERAL_FEEDBACK_CHANNELS}


__all__ = ["VisceralSignal", "VISCERAL_FEEDBACK_CHANNELS", "baseline_comfort_map"]