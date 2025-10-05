"""Head and facial subsystem metadata for Vex."""

from .cranial_bones import CRANIAL_BONES, CranialBone, iter_cranial_bones
from .facial_muscles import FACIAL_MUSCLES, FacialMuscle, iter_facial_muscles
from .expressions import FACIAL_EXPRESSIONS, FacialExpression, iter_facial_expressions
from .eyes import EYE_RIG_TARGETS, EyeModule, EyeRigTarget, iter_eye_rig_targets

__all__ = [
    "CranialBone",
    "CRANIAL_BONES",
    "iter_cranial_bones",
    "FacialMuscle",
    "FACIAL_MUSCLES",
    "iter_facial_muscles",
    "FacialExpression",
    "FACIAL_EXPRESSIONS",
    "iter_facial_expressions",
    "EyeRigTarget",
    "EYE_RIG_TARGETS",
    "iter_eye_rig_targets",
    "EyeModule",
]