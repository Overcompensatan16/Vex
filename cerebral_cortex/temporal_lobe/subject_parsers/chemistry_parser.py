"""Simple regex-based chemistry parser.

This module extracts basic chemical information from text
and converts it into structured fact dictionaries suitable
for the fact generator. It intentionally avoids complex
or "hard" chemistry topics.
"""

from __future__ import annotations

import json
import os
import re
from typing import List, Dict, Optional
from datetime import datetime, timezone


# Central registry for discovered compounds
COMPOUND_REGISTRY_PATH = os.path.join(
    "E:", "AI_Memory_Stores", "Chemistry", "known_compounds", "known_compounds.jsonl"
)

# Audit file for records not routed directly
AUDIT_PATH = os.path.join("external_store", "chemistry_audit.jsonl")

# Regex patterns
FORMULA_RE = re.compile(r"\b([A-Z][a-z]?\d*)+\b")
REACTION_RE = re.compile(r"(\+|→|=|->|⇌)")
TERMS_RE = re.compile(r"\b(acid|base|catalyst|oxidize|reduce)\b", re.IGNORECASE)


def _normalize_name(name: str) -> str:
    """Normalize a compound name for de-duplication."""
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def _load_compound_registry(path: str) -> Dict[str, Dict]:
    """Load the compound registry from JSONL into a dictionary keyed by name."""
    registry: Dict[str, Dict] = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
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


def _load_known_compounds(path: str) -> Dict[str, str]:
    """Build a mapping from formula to name using the compound registry."""
    mapping: Dict[str, str] = {}
    for entry in _load_compound_registry(path).values():
        name = entry.get("name")
        formula = entry.get("formula")
        if name and formula:
            mapping[formula] = name
    return mapping


def _append_compound_entry(entry: Dict, update_existing: bool = False) -> None:
    """Append a new compound entry to the registry with optional update."""
    os.makedirs(os.path.dirname(COMPOUND_REGISTRY_PATH), exist_ok=True)
    registry = _load_compound_registry(COMPOUND_REGISTRY_PATH)
    key = _normalize_name(entry.get("name", ""))
    if not key:
        return
    if key in registry:
        if not update_existing:
            return
        registry[key].update(entry)
        with open(COMPOUND_REGISTRY_PATH, "w", encoding="utf-8") as f:
            for record in registry.values():
                f.write(json.dumps(record) + "\n")
        return
    with open(COMPOUND_REGISTRY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


KNOWN_COMPOUNDS = _load_known_compounds(COMPOUND_REGISTRY_PATH)


def _write_audit(record: Dict) -> None:
    os.makedirs(os.path.dirname(AUDIT_PATH), exist_ok=True)
    with open(AUDIT_PATH, "a", encoding="utf-8") as audit_file:
        audit_file.write(json.dumps(record) + "\n")


def parse_chemistry_text(text: str, source_file: Optional[str] = None) -> List[Dict]:
    """Parse text and return structured chemistry fact dictionaries.

    Parameters
    ----------
    text: str
        Input text containing chemistry information.
    source_file: Optional[str]
        Optional source filename for compound registry entries.
    """
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        formulas = FORMULA_RE.findall(sent)
        reaction = REACTION_RE.search(sent)
        term_match = TERMS_RE.search(sent)

        if not (formulas or reaction or term_match):
            continue

        now = datetime.now(timezone.utc).isoformat()
        record: Dict = {
            "type": "chemistry",
            "subtype": None,
            "source": "chemistry_parser",
            "fact": sent,
            "timestamp": now,
            "confidence": 0.5,
        }

        if reaction:
            parts = re.split(REACTION_RE, sent)
            reactants = parts[0].strip().split("+") if len(parts) > 1 else []
            products = parts[-1].strip().split("+") if len(parts) > 2 else []
            record.update({
                "subtype": "reaction",
                "reactants": [r.strip() for r in reactants if r.strip()],
                "products": [p.strip() for p in products if p.strip()],
                "confidence": 0.9,
            })
        elif formulas:
            normalized = [f.strip() for f in formulas]
            known = [f for f in normalized if f in KNOWN_COMPOUNDS]
            record.update({
                "subtype": "compound",
                "compounds": normalized,
                "known_compounds": known,
                "confidence": 0.8 if known else 0.6,
            })

            # Log compounds to the central registry
            for formula in normalized:
                compound_name = KNOWN_COMPOUNDS.get(formula, formula)
                entry = {
                    "name": compound_name,
                    "type": None,
                    "formula": formula,
                    "purpose": [],
                    "legality": {"us": None, "eu": None, "schedule": None},
                    "source_text": sent,
                    "source_file": source_file,
                    "origin": "chemistry_parser",
                    "timestamp": now,
                    "aliases": [],
                    "discovery": None,
                    "uses": [],
                    "toxicity": None,
                    "legal_notes": None,
                }
                _append_compound_entry(entry)
        elif term_match:
            record.update({
                "subtype": "term",
                "term": term_match.group(0).lower(),
                "confidence": 0.6,
            })
        results.append(record)
        _write_audit(record)

    return results
