from collections import deque
from typing import List, Dict, Optional
import json


class ContextTracker:
    """
    Maintains a bounded history of processed cognitive or linguistic entries.
    Can be used in any module to hold short-term context before memory storage.
    """

    def __init__(self, max_size: int = 10, name: Optional[str] = None):
        if max_size <= 0:
            raise ValueError("max_size must be greater than zero.")
        self._buffer = deque(maxlen=max_size)
        self.name = name or "unnamed_context_tracker"

    def add(self, item: Dict) -> None:
        """
        Add a parsed entry (typically a linguistic or symbolic structure) to history.

        Parameters
        ----------
        item : dict
            The structured representation to add.
        """
        if not isinstance(item, dict):
            raise TypeError("Only dictionary entries can be added to context.")
        self._buffer.append(item)

    def recent(self) -> List[Dict]:
        """
        Return the current list of recent entries in order of addition.

        Returns
        -------
        list of dict
            Most recent context entries.
        """
        return list(self._buffer)

    def export_json(self, path: str) -> None:
        """
        Export the current buffer contents to a JSON file.

        Parameters
        ----------
        path : str
            File path to save the JSON snapshot.
        """
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.recent(), f, indent=2)
        except Exception as e:
            raise IOError(f"[{self.name}] Failed to export context to {path}: {e}")

    def load_json(self, path: str) -> None:
        """
        Load previously saved context into the buffer from a JSON file.

        Parameters
        ----------
        path : str
            Path to the JSON file to load from.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                items = json.load(f)
            for item in items:
                self.add(item)
        except Exception as e:
            raise IOError(f"[{self.name}] Failed to load context from {path}: {e}")


__all__ = ["ContextTracker"]
