"""Joint definitions for pelvic articulations including the hip and pubic symphysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class PelvicJoint:
    """Description of a pelvic joint and its stabilizing structures."""

    name: str
    joint_type: str
    supporting_structures: Tuple[str, ...]
    range_of_motion: Dict[str, float]
    neurovascular_links: Tuple[str, ...]


PELVIC_JOINTS: Tuple[PelvicJoint, ...] = (
    PelvicJoint(
        name="Acetabulofemoral joint",
        joint_type="Ball and socket synovial",
        supporting_structures=(
            "Iliofemoral ligament",
            "Pubofemoral ligament",
            "Ischiofemoral ligament",
            "Labrum acetabulare",
        ),
        range_of_motion={
            "flexion": 120.0,
            "extension": 30.0,
            "abduction": 45.0,
            "adduction": 30.0,
            "external_rotation": 45.0,
            "internal_rotation": 40.0,
        },
        neurovascular_links=(
            "Femoral nerve",
            "Obturator nerve",
            "Medial circumflex femoral artery",
        ),
    ),
    PelvicJoint(
        name="Pubic symphysis",
        joint_type="Secondary cartilaginous",
        supporting_structures=(
            "Superior pubic ligament",
            "Inferior pubic ligament",
            "Interpubic fibrocartilage",
        ),
        range_of_motion={"separation": 2.0, "shear": 1.0},
        neurovascular_links=("Ilioinguinal nerve", "External pudendal vessels"),
    ),
    PelvicJoint(
        name="Sacroiliac joint",
        joint_type="Synovial (anterior) and syndesmosis (posterior)",
        supporting_structures=(
            "Anterior sacroiliac ligament",
            "Posterior sacroiliac ligament",
            "Sacrotuberous ligament",
            "Sacrospinous ligament",
        ),
        range_of_motion={"nutation": 4.0, "counternutation": 4.0},
        neurovascular_links=("Lumbosacral trunk", "Superior gluteal vessels"),
    ),
)


__all__ = ["PelvicJoint", "PELVIC_JOINTS"]