"""Eye rig metadata and optic stack stub."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Optional, Tuple

from audit.audit_logger import AuditLogger


@dataclass(frozen=True)
class EyeRigTarget:
    """Represents a controllable eye rig element."""

    name: str
    rig_target: str
    degrees_of_freedom: Tuple[str, ...]
    default_range: Tuple[float, float]
    notes: str = ""


EYE_RIG_TARGETS: tuple[EyeRigTarget, ...] = (
    EyeRigTarget(
        name="eye_left_gimbal",
        rig_target="CTRL_Eye_L",
        degrees_of_freedom=("yaw", "pitch"),
        default_range=(-35.0, 35.0),
        notes="Primary aim control for left eye aligned with optic nerve stub.",
    ),
    EyeRigTarget(
        name="eye_right_gimbal",
        rig_target="CTRL_Eye_R",
        degrees_of_freedom=("yaw", "pitch"),
        default_range=(-35.0, 35.0),
        notes="Primary aim control for right eye aligned with optic nerve stub.",
    ),
    EyeRigTarget(
        name="eyelid_upper",
        rig_target="CTRL_EyelidUpper",
        degrees_of_freedom=("open_close",),
        default_range=(0.0, 1.0),
        notes="Supports blink and alertness cues.",
    ),
    EyeRigTarget(
        name="eyelid_lower",
        rig_target="CTRL_EyelidLower",
        degrees_of_freedom=("open_close",),
        default_range=(0.0, 1.0),
        notes="Allows squint compression from affect.face.squint signals.",
    ),
)


class EyeModule:
    """Minimal eye module with optic stack handshake."""

    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        self.audit_logger = audit_logger or AuditLogger("audit/eye_module_log.jsonl")
        self._optic_stack: object | None = None
        self.audit_logger.log_event(
            "eye_module_initialized",
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "targets": [target.name for target in EYE_RIG_TARGETS],
            },
        )

    def attach_optic_stack(self, optic_stack: object) -> dict:
        """Attach a future optic nerve/vision processing stack."""

        self._optic_stack = optic_stack
        descriptor = getattr(optic_stack, "name", optic_stack.__class__.__name__)
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stack_descriptor": descriptor,
        }
        self.audit_logger.log_event("optic_stack_attached", payload)
        return payload

    @property
    def optic_stack(self) -> object | None:
        """Return the currently attached optic stack if any."""

        return self._optic_stack


def iter_eye_rig_targets() -> Iterable[EyeRigTarget]:
    """Iterate configured eye rig targets."""

    return iter(EYE_RIG_TARGETS)


__all__ = [
    "EyeRigTarget",
    "EYE_RIG_TARGETS",
    "iter_eye_rig_targets",
    "EyeModule",
]