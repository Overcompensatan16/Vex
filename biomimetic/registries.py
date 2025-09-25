"""Aggregate biomimetic registry metadata from external JSON contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Mapping, Any

BIOMIMETIC_ROOT = Path(__file__).resolve().parent
_REGISTRY_FILENAME = "registry.json"


def _load_single_registry(path: Path) -> Dict[str, Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError(f"Registry file {path} must contain an object mapping")
        # Normalise keys to lowercase to satisfy registry constraints while
        # preserving the declared metadata.
        normalised: Dict[str, Dict[str, Any]] = {}
        for key, meta in data.items():
            lower_key = key.lower()
            if lower_key in normalised:
                raise ValueError(f"Duplicate signal path {lower_key} in {path}")
            if not isinstance(meta, Mapping):
                raise ValueError(f"Registry entry {key} in {path} must be a mapping")
            normalised[lower_key] = dict(meta)
            normalised[lower_key]["declared_path"] = key
        return normalised


def load_biomimetic_registry_map() -> Dict[str, Dict[str, Any]]:
    """Load every ``registry.json`` contract beneath :mod:`biomimetic`."""

    aggregated: Dict[str, Dict[str, Any]] = {}
    for json_file in BIOMIMETIC_ROOT.rglob(_REGISTRY_FILENAME):
        registry_data = _load_single_registry(json_file)
        for path, meta in registry_data.items():
            if path in aggregated:
                raise ValueError(
                    f"Duplicate biomimetic signal path {path} defined in {json_file}"
                )
            aggregated[path] = meta
    return aggregated


__all__ = ["load_biomimetic_registry_map"]