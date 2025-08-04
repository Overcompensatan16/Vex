"""Simple regex-based economics parser.

This module extracts basic economic definitions and causal relationships
from text. It focuses on macro and micro economics patterns, including
statements like "Inflation is ...".
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List

# Keyword sets for macro and micro economic terms
MACRO_TERMS = {
    "inflation",
    "gdp",
    "unemployment",
    "interest rate",
    "fiscal policy",
    "monetary policy",
}

MICRO_TERMS = {
    "supply",
    "demand",
    "price",
    "cost",
    "market",
    "utility",
}

# Pattern for definitions like "Term is ..."
DEFINITION_RE = re.compile(
    r"\b([A-Za-z\s]+?)\s+is\s+(?:an|a|the)\s+([^.,;]+)",
    re.IGNORECASE,
)

# Specific pattern to capture "Inflation is ..." statements
INFLATION_RE = re.compile(r"\bInflation\s+is\s+([^.,;]+)", re.IGNORECASE)

# Pattern for causal relationships like "X leads to Y"
CAUSAL_RE = re.compile(
    r"\b([A-Za-z\s]+?)\s+(leads to|causes|results in|increases|decreases)\s+([A-Za-z\s]+?)(?=[.,;!?]|$)",
    re.IGNORECASE,
)


def parse_econ_text(text: str) -> List[Dict]:
    """Parse text and return structured economics fact dictionaries."""
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "economics",
            "source": "econ_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Check for explicit inflation definition
        infl_match = INFLATION_RE.search(sent)
        if infl_match:
            definition = infl_match.group(1).strip()
            record.update(
                {
                    "subtype": "definition",
                    "term": "inflation",
                    "definition": definition,
                    "domain": "macro",
                    "confidence": 0.95,
                }
            )
            results.append(record)
            continue

        # General definition pattern
        def_match = DEFINITION_RE.search(sent)
        if def_match:
            term = def_match.group(1).strip()
            definition = def_match.group(2).strip()
            domain = (
                "macro"
                if term.lower() in MACRO_TERMS
                else "micro" if term.lower() in MICRO_TERMS else "unknown"
            )
            record.update(
                {
                    "subtype": "definition",
                    "term": term,
                    "definition": definition,
                    "domain": domain,
                    "confidence": 0.9,
                }
            )
            results.append(record)
            continue

        # Causal relationship pattern
        causal_match = CAUSAL_RE.search(sent)
        if causal_match:
            cause = causal_match.group(1).strip()
            effect = causal_match.group(3).strip()
            cause_lower = cause.lower()
            effect_lower = effect.lower()
            if any(term in cause_lower or term in effect_lower for term in MACRO_TERMS):
                domain = "macro"
            elif any(term in cause_lower or term in effect_lower for term in MICRO_TERMS):
                domain = "micro"
            else:
                domain = "unknown"
            record.update(
                {
                    "subtype": "causal_relationship",
                    "cause": cause,
                    "effect": effect,
                    "domain": domain,
                    "confidence": 0.85,
                }
            )
            results.append(record)
            continue

        record.update({"subtype": "other", "confidence": 0.1})
        results.append(record)

    return results


__all__ = ["parse_econ_text"]
