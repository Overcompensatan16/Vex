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

from cerebral_cortex.source_handlers.transformer_fact_extractor import (
    load_known_compound_map,
    record_compound,
)

# Audit file for records not routed directly
AUDIT_PATH = os.path.join("external_store", "chemistry_audit.jsonl")

# Regex patterns
FORMULA_RE = re.compile(r"\b([A-Z][a-z]?\d*)+\b")
REACTION_RE = re.compile(r"(\+|\u2192|=|->|\u21cc)")
TERMS_RE = re.compile(r"\b(acid|base|catalyst|oxidize|reduce)\b", re.IGNORECASE)

# Load compound map
KNOWN_COMPOUNDS = load_known_compound_map()


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
        record: Dict = {
            "type": "chemistry",
            "source": "chemistry_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        formulas = FORMULA_RE.findall(sent)
        reaction = REACTION_RE.search(sent)
        term_match = TERMS_RE.search(sent)

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

            for formula in normalized:
                compound_name = KNOWN_COMPOUNDS.get(formula, formula)
                record_compound(
                    name=compound_name,
                    formula=formula,
                    source_text=sent,
                    source_file=source_file,
                    origin="chemistry_parser",
                    timestamp=record["timestamp"],
                )

        elif term_match:
            record.update({
                "subtype": "term",
                "term": term_match.group(0).lower(),
                "confidence": 0.6,
            })

        results.append(record)
        _write_audit(record)

    return results
