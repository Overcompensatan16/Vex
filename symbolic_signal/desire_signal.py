"""Dataclasses for desire signals."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class DesireSignal:
    """Symbolic output from the DesireEngine."""

    module: str
    confidence: float
    type: str
    source: str = "desire_engine"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def as_dict(self) -> dict:
        return {
            "module": self.module,
            "confidence": self.confidence,
            "type": self.type,
            "source": self.source,
            "timestamp": self.timestamp,
        }


__all__ = ["DesireSignal"]