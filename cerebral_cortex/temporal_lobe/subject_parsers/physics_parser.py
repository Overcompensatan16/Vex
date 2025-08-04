"""Simple regex-based physics parser.

This module extracts basic physics information from text
and converts it into structured fact dictionaries suitable
for downstream processing. It intentionally avoids complex
or highly technical physics topics.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Known physical constants mapped to human-readable names
KNOWN_CONSTANTS: Dict[str, str] = {
    "c": "speed of light",
    "G": "gravitational constant",
    "h": "Planck constant",
    "ħ": "reduced Planck constant",
    "e": "elementary charge",
    "k": "Boltzmann constant",
    "R": "gas constant",
    "g": "standard gravity",
}

# Common physics keywords for simple topical detection
PHYSICS_KEYWORDS = {
    "force",
    "mass",
    "energy",
    "momentum",
    "velocity",
    "acceleration",
    "gravity",
    "wave",
    "particle",
    "quantum",
    "relativity",
    "electric",
    "magnetic",
    "pressure",
    "temperature",
    "current",
    "voltage",
    "resistance",
}

# Named physical laws for identification in text
NAMED_LAWS: Dict[str, str] = {
    "newton's first law": "law of inertia",
    "newton's second law": "force equals mass times acceleration",
    "newton's third law": "every action has an equal and opposite reaction",
    "law of universal gravitation": "gravitational attraction between masses",
    "ohm's law": "voltage equals current times resistance",
    "hooke's law": "force proportional to spring extension",
    "boyle's law": "pressure inversely proportional to volume",
    "coulomb's law": "electrostatic force relation",
}

# Regex patterns for well known equations
EQUATION_PATTERNS: Dict[re.Pattern, str] = {
    re.compile(r"\bF\s*=\s*ma\b", re.IGNORECASE): "Newton's second law",
    re.compile(r"\bE\s*=\s*mc\^2\b", re.IGNORECASE): "Mass-energy equivalence",
    re.compile(r"\bV\s*=\s*IR\b", re.IGNORECASE): "Ohm's law",
    re.compile(r"\bF\s*=\s*kx\b", re.IGNORECASE): "Hooke's law",
    re.compile(r"\bPV\s*=\s*nRT\b", re.IGNORECASE): "Ideal gas law",
}

# Generic equation detector
GENERIC_EQUATION_RE = re.compile(r"[A-Za-z\d\s^*/()+-]+=[A-Za-z\d\s^*/()+-]+")


def parse_physics_text(text: str, source_file: Optional[str] = None) -> List[Dict]:
    """Parse text and return structured physics fact dictionaries.

    Parameters
    ----------
    text: str
        Input text containing physics information.
    source_file: Optional[str]
        Optional source filename for context or auditing.
    """
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "physics",
            "source": "physics_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        lowered = sent.lower()

        # Check for named laws
        law_match = next((law for law in NAMED_LAWS if law in lowered), None)
        if law_match:
            record.update(
                {
                    "subtype": "law",
                    "name": law_match,
                    "description": NAMED_LAWS[law_match],
                    "confidence": 0.9,
                }
            )
            results.append(record)
            continue

        # Check for well known equations
        equation_match = None
        for pattern, name in EQUATION_PATTERNS.items():
            if pattern.search(sent):
                equation_match = name
                record.update(
                    {
                        "subtype": "equation",
                        "name": name,
                        "equation": pattern.pattern.replace("\\b", ""),
                        "confidence": 0.85,
                    }
                )
                break

        # Generic equation detection if no named equation matched
        if not equation_match and GENERIC_EQUATION_RE.search(sent):
            constants = [
                sym
                for sym in KNOWN_CONSTANTS
                if re.search(rf"\b{re.escape(sym)}\b", sent)
            ]
            record.update(
                {
                    "subtype": "equation",
                    "equation": sent,
                    "constants": constants,
                    "confidence": 0.6 if constants else 0.5,
                }
            )
            results.append(record)
            continue

        # Keyword or constant mentions
        keywords = [
            kw
            for kw in PHYSICS_KEYWORDS
            if re.search(rf"\b{re.escape(kw)}\b", lowered)
        ]
        constants = [
            sym
            for sym in KNOWN_CONSTANTS
            if re.search(rf"\b{re.escape(sym)}\b", sent)
        ]
        if keywords or constants:
            record.update(
                {
                    "subtype": "keyword",
                    "keywords": keywords,
                    "constants": constants,
                    "confidence": 0.4,
                }
            )
        else:
            record.update({"subtype": "other", "confidence": 0.1})

        results.append(record)

    return results


__all__ = ["parse_physics_text"]
