from __future__ import annotations

from datetime import datetime, timezone
from typing import List


class SomaticResponse:
    """Simulate body-like fear reactions."""

    def __init__(self) -> None:
        self.current_state: List[str] = []
        self.last_update: str | None = None
        print("[SomaticResponse] Initialized.")

    def simulate_response(self, fear_level: str, responses: list[str]) -> None:
        """Set the current simulated body response."""
        self.current_state = responses
        self.last_update = datetime.now(timezone.utc).isoformat()
        print(f"[SomaticResponse] {fear_level} -> {responses}")

    def get_current_feelings(self) -> list[str]:
        return list(self.current_state)

    def clear_response(self) -> None:
        self.current_state.clear()
        print("[SomaticResponse] Cleared response state.")


__all__ = ["SomaticResponse"]