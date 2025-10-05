"""Torso skin and surface metadata definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass(frozen=True)
class TorsoSkinRegion:
    """Describes a surface patch of torso skin for rig integration."""

    name: str
    rig_bind: str
    surface_area_cm2: float
    sensory_clusters: Tuple[str, ...]
    notes: str = ""


TORSO_SKIN_REGIONS: List[TorsoSkinRegion] = [
    TorsoSkinRegion(
        name="sternal_plate",
        rig_bind="BIND_SternumSurface",
        surface_area_cm2=420.0,
        sensory_clusters=("cutaneous.chest", "cutaneous.sternum"),
        notes="Handles chest compression morphs and tactile reflex routing.",
    ),
    TorsoSkinRegion(
        name="abdominal_wall",
        rig_bind="BIND_AbdomenSurface",
        surface_area_cm2=560.0,
        sensory_clusters=("cutaneous.abdomen",),
        notes="Captures breathing distension and gut micromotion.",
    ),
    TorsoSkinRegion(
        name="upper_back",
        rig_bind="BIND_UpperBackSurface",
        surface_area_cm2=480.0,
        sensory_clusters=("cutaneous.upper_back", "proprioceptive.scapular"),
        notes="Feeds scapular slide shading and postural sway textures.",
    ),
    TorsoSkinRegion(
        name="lower_back",
        rig_bind="BIND_LowerBackSurface",
        surface_area_cm2=360.0,
        sensory_clusters=("cutaneous.lower_back",),
        notes="Supports lumbar flexion wrinkling and brace tension cues.",
    ),
]


def iter_torso_skin_regions() -> Iterable[TorsoSkinRegion]:
    """Iterate over configured torso skin regions."""

    return iter(TORSO_SKIN_REGIONS)


__all__ = ["TorsoSkinRegion", "TORSO_SKIN_REGIONS", "iter_torso_skin_regions"]