from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, List


@dataclass
class SymbolicSignal:
    """Unified signal object for sensory data."""

    data: Any
    modality: str
    source: str
    tags: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def as_dict(self) -> dict:
        return {
            "data": self.data,
            "modality": self.modality,
            "source": self.source,
            "tags": self.tags,
            "timestamp": self.timestamp,
        }


__all__ = ["SymbolicSignal"]
