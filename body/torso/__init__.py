"""Torso musculoskeletal modules."""

from .bones import TORSO_BONES, TorsoBone, iter_torso_bones
from .core import TorsoModule
from .ligaments import TORSO_LIGAMENTS, TorsoLigament, iter_torso_ligaments
from .muscles import TORSO_MUSCLES, TorsoMuscle, iter_torso_muscles
from .skin import TORSO_SKIN_REGIONS, TorsoSkinRegion, iter_torso_skin_regions

__all__ = [
    "TorsoModule",
    "TorsoBone",
    "TorsoLigament",
    "TorsoMuscle",
    "TorsoSkinRegion",
    "TORSO_BONES",
    "TORSO_LIGAMENTS",
    "TORSO_MUSCLES",
    "TORSO_SKIN_REGIONS",
    "iter_torso_bones",
    "iter_torso_ligaments",
    "iter_torso_muscles",
    "iter_torso_skin_regions",
]