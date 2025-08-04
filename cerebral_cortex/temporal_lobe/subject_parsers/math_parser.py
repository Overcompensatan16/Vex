"""Simple regex-based mathematics parser.

This module extracts basic mathematical statements from text
and converts them into structured fact dictionaries for the
fact generator. It intentionally keeps the logic lightweight.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import List, Dict

# Common math-related keywords for loose detection
MATH_KEYWORDS = [
    "theorem",
    "lemma",
    "corollary",
    "proposition",
    "definition",
    "define",
    "equation",
    "integral",
    "derivative",
]

# Named mathematical laws/theorems of interest
NAMED_LAWS = [
    "Pythagorean theorem",
    "Law of Sines",
    "Law of Cosines",
    "Fundamental theorem of calculus",
    "Law of Large Numbers",
    "Euler's formula",
]

# Regular expressions for specific constructs
DEFINITION_RE = re.compile(r"\b(definition|define|is defined as)\b", re.IGNORECASE)
THEOREM_RE = re.compile(r"\b(theorem|lemma|corollary|proposition)\b", re.IGNORECASE)
EQUATION_RE = re.compile(r"[^=]+=[^=]+")


def parse_math_text(text: str) -> List[Dict]:
    """Parse text and return structured math fact dictionaries."""
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "math",
            "source": "math_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Named laws
        law_match = next((law for law in NAMED_LAWS if law.lower() in sent.lower()), None)
        if law_match:
            record.update({
                "subtype": "law",
                "law": law_match,
                "confidence": 0.9,
            })
        elif EQUATION_RE.search(sent):
            record.update({
                "subtype": "equation",
                "expression": EQUATION_RE.search(sent).group(0),
                "confidence": 0.85,
            })
        elif THEOREM_RE.search(sent):
            record.update({
                "subtype": "theorem",
                "theorem": THEOREM_RE.search(sent).group(0).lower(),
                "confidence": 0.8,
            })
        elif DEFINITION_RE.search(sent):
            record.update({
                "subtype": "definition",
                "definition": sent,
                "confidence": 0.7,
            })
        elif any(kw in sent.lower() for kw in MATH_KEYWORDS):
            matched = [kw for kw in MATH_KEYWORDS if kw in sent.lower()]
            record.update({
                "subtype": "keyword",
                "keywords": matched,
                "confidence": 0.5,
            })

        results.append(record)

    return results


__all__ = ["parse_math_text"]
