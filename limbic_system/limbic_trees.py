import json
import os
import shutil


def _ensure_tagging_file(path: str) -> None:
    """Create ``path`` by copying local tagging_data.json if missing."""
    norm = path.replace("\\", "/")
    if os.path.exists(norm):
        return
    local = os.path.join(os.path.dirname(__file__), "..", "hippocampus", "tagging_data.json")
    if os.path.exists(local):
        try:
            os.makedirs(os.path.dirname(norm), exist_ok=True)
            shutil.copy(local, norm)
        except Exception:
            pass


class SephirotTree:
    """Representation of the Tree of Life."""

    def __init__(self, tagging_path: str = r"E:\AI_Memory_Stores\emotion\tagging_data.json") -> None:
        self.nodes = [
            "Keter",
            "Chokmah",
            "Binah",
            "Chesed",
            "Gevurah",
            "Tiphareth",
            "Netzach",
            "Hod",
            "Yesod",
            "Malkuth",
        ]
        self.paths: dict[str, list[str]] = {}
        self.affinity: dict[str, dict] = {}
        _ensure_tagging_file(tagging_path)
        self._load_affinity(tagging_path)

    def _load_affinity(self, path: str) -> None:
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.affinity = data.get("Sephirot", {})
        except Exception:
            self.affinity = {}


class QliphothTree:
    """Representation of the Tree of Shadow."""

    def __init__(self, tagging_path: str = r"E:\AI_Memory_Stores\emotion\tagging_data.json") -> None:
        self.nodes = [
            "Thaumiel",
            "Chagidiel",
            "Belial",
            "Sathariel",
            "Gamaliel",
            "Golachab",
            "Togarini",
            "Harab Serapel",
            "Samael",
            "Naamah",
            "Lilith",
        ]
        self.paths: dict[str, list[str]] = {}
        self.affinity: dict[str, dict] = {}
        _ensure_tagging_file(tagging_path)
        self._load_affinity(tagging_path)

    def _load_affinity(self, path: str) -> None:
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.affinity = data.get("Qliphoth", {})
        except Exception:
            self.affinity = {}