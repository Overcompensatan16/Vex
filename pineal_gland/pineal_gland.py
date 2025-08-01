"""Synthetic pineal gland module."""

from __future__ import annotations

import math
import time
from typing import Optional


# Capture module import time as the start of the internal 24h cycle
_CYCLE_START = time.monotonic()


def _cycle_position(seconds: Optional[float] = None, cycle_seconds: float = 86400) -> float:
    """Return elapsed seconds within a cycle.

    This helper allows overriding the time source for testing.
    """
    current = seconds if seconds is not None else time.monotonic()
    return (current - _CYCLE_START) % cycle_seconds


def get_circadian_scalar(cycle_seconds: float = 86400, offset: float = 0.0, *, seconds: Optional[float] = None) -> float:
    """Return a scalar representing the current circadian wakefulness level.

    The value ranges from ``0.0`` (asleep) to ``1.0`` (fully awake). It is
    derived from a cosine curve mapped over an internal 24 hour cycle. ``offset``
    can be used to shift the phase of the cycle in seconds. ``seconds`` is
    primarily for testing and overrides the monotonic time source.
    """
    pos = (_cycle_position(seconds, cycle_seconds) + offset) % cycle_seconds
    theta = (pos / cycle_seconds) * 2 * math.pi
    # Cosine shifted so midnight ~ 0.0 and midday ~ 1.0
    return (math.cos(theta + math.pi) + 1) / 2


__all__ = ["get_circadian_scalar"]