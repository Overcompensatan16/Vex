"""Utilities for enriching parsed data and updating global registries."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, List

# Path to the universal compound registry
COMPOUND_REGISTRY_PATH = os.path.join(
    "E:", "AI_Memory_Stores", "chemistry", "known_compounds.jsonl"
)


def _normalize_name(name: str) -> str:
    """Normalize a compound name for de-duplication."""
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def _load_registry() -> Dict[str, Dict]:
    """Load the compound registry into a dictionary keyed by normalized name."""
    registry: Dict[str, Dict] = {}
    try:
        with open(COMPOUND_REGISTRY_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                name = entry.get("name")
                if not name:
                    continue
                registry[_normalize_name(name)] = entry
    except FileNotFoundError:
        pass
    return registry


def load_known_compound_map() -> Dict[str, str]:
    """Build a mapping from formula to canonical compound name."""
    mapping: Dict[str, str] = {}
    for entry in _load_registry().values():
        name = entry.get("name")
        formula = entry.get("formula")
        if name and formula:
            mapping[formula] = name
    return mapping


def append_compound_entry(entry: Dict, update_existing: bool = False) -> None:
    """Append or update a compound entry in the global registry."""
    os.makedirs(os.path.dirname(COMPOUND_REGISTRY_PATH), exist_ok=True)
    registry = _load_registry()
    key = _normalize_name(entry.get("name", ""))
    if not key:
        return
    existing = registry.get(key)
    if existing:
        changed = False
        # Merge simple scalar fields if missing in existing
        for field in [
            "type",
            "formula",
            "discovery",
            "field",
            "safety",
            "source_text",
            "source_file",
            "origin",
            "timestamp",
        ]:
            value = entry.get(field)
            if value and not existing.get(field):
                existing[field] = value
                changed = True
        # Merge list fields uniquely
        for list_field in ["aliases", "purpose", "uses"]:
            values = entry.get(list_field, [])
            if values:
                existing.setdefault(list_field, [])
                before = set(existing[list_field])
                new_items = [v for v in values if v not in before]
                if new_items:
                    existing[list_field].extend(new_items)
                    changed = True
        # Merge legality subfields
        if entry.get("legality"):
            existing.setdefault("legality", {"us": "", "eu": "", "schedule": None})
            for k, v in entry["legality"].items():
                if v and not existing["legality"].get(k):
                    existing["legality"][k] = v
                    changed = True
        if not changed and not update_existing:
            return
        registry[key] = existing
        with open(COMPOUND_REGISTRY_PATH, "w", encoding="utf-8") as f:
            for record in registry.values():
                f.write(json.dumps(record) + "\n")
    else:
        with open(COMPOUND_REGISTRY_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


def record_compound(
    name: str,
    formula: str,
    source_text: str,
    source_file: str | None,
    origin: str,
    *,
    type_: str | None = None,
    aliases: List[str] | None = None,
    purpose: List[str] | None = None,
    legality: Dict[str, str | None] | None = None,
    field: str | None = None,
    safety: str | None = None,
    uses: List[str] | None = None,
    discovery: str | None = None,
    timestamp: str | None = None,
) -> None:
    """Convenience wrapper to build and append a compound record."""
    entry = {
        "name": name,
        "type": type_,
        "formula": formula,
        "aliases": aliases or [],
        "purpose": purpose or [],
        "legality": legality or {"us": "", "eu": "", "schedule": None},
        "field": field or "",
        "safety": safety or "",
        "uses": uses or [],
        "discovery": discovery or "",
        "source_text": source_text,
        "source_file": source_file,
        "origin": origin,
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
    }
    append_compound_entry(entry)


def transform_text(text: str) -> str:
    """Placeholder transformer hook that currently returns text unchanged."""
    return text

__all__ = [
    "COMPOUND_REGISTRY_PATH",
    "append_compound_entry",
    "load_known_compound_map",
    "record_compound",
    "transform_text",
]