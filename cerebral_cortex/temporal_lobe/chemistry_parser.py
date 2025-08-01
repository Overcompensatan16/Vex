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
from typing import List, Dict
from datetime import datetime, timezone


# Path to a small dictionary of known compounds in JSONL form
COMPOUND_DICT_PATH = os.path.join(os.path.dirname(__file__), "known_compounds.jsonl")

# Audit file for records not routed directly
AUDIT_PATH = os.path.join("external_store", "chemistry_audit.jsonl")

# Regex patterns
FORMULA_RE = re.compile(r"\b([A-Z][a-z]?\d*)+\b")
REACTION_RE = re.compile(r"(\+|→|=|->|⇌)")
TERMS_RE = re.compile(r"\b(acid|base|catalyst|oxidize|reduce)\b", re.IGNORECASE)


def _load_known_compounds(path: str) -> Dict[str, str]:
    """Load dictionary of known compounds from a JSONL file."""
    compounds: Dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    formula = entry.get("formula")
                    name = entry.get("name")
                    if formula and name:
                        compounds[formula] = name
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        pass
    return compounds


KNOWN_COMPOUNDS = _load_known_compounds(COMPOUND_DICT_PATH)


def _write_audit(record: Dict) -> None:
    os.makedirs(os.path.dirname(AUDIT_PATH), exist_ok=True)
    with open(AUDIT_PATH, "a", encoding="utf-8") as audit_file:
        audit_file.write(json.dumps(record) + "\n")


def parse_chemistry_text(text: str) -> List[Dict]:
    """Parse text and return structured chemistry fact dictionaries."""
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        formulas = FORMULA_RE.findall(sent)
        reaction = REACTION_RE.search(sent)
        term_match = TERMS_RE.search(sent)

        if not (formulas or reaction or term_match):
            continue

        record: Dict = {
            "type": "chemistry",
            "subtype": None,
            "source": "chemistry_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
        elif term_match:
            record.update({
                "subtype": "term",
                "term": term_match.group(0).lower(),
                "confidence": 0.6,
            })
        results.append(record)
        _write_audit(record)

    return results
