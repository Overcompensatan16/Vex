"""Simple regex-based psychology parser.

This module focuses on cognitive and behavioral terms,
mental states, and theories. It extracts psychology-related
statements from text and converts them into structured
fact dictionaries for downstream processing.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List

# Keyword lists for different psychological concepts
COGNITIVE_TERMS = {
    "memory",
    "attention",
    "perception",
    "learning",
    "language",
    "cognition",
    "problem solving",
}

BEHAVIORAL_TERMS = {
    "reinforcement",
    "conditioning",
    "stimulus",
    "response",
    "habit",
    "punishment",
}

MENTAL_STATES = {
    "anxiety",
    "depression",
    "anger",
    "fear",
    "happiness",
    "stress",
    "motivation",
}

THEORY_KEYWORDS = {
    "behaviorism",
    "psychoanalysis",
    "cognitive dissonance",
    "attachment theory",
    "social learning theory",
    "big five",
}

# Pattern for mental disorder descriptions ("X is a mental disorder characterized by Y")
MENTAL_DISORDER_RE = re.compile(
    r"\b([A-Za-z\s]+?)\s+is a mental disorder characterized by\s+([^.]+)",
    re.IGNORECASE,
)


def parse_psychology_text(text: str) -> List[Dict]:
    """Parse text and return structured psychology fact dictionaries."""
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "psychology",
            "source": "psychology_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        lowered = sent.lower()

        disorder_match = MENTAL_DISORDER_RE.search(sent)
        if disorder_match:
            disorder = disorder_match.group(1).strip()
            description = disorder_match.group(2).strip()
            record.update(
                {
                    "subtype": "mental_disorder",
                    "disorder": disorder,
                    "description": description,
                    "confidence": 0.9,
                }
            )
            results.append(record)
            continue

        mental_states = [
            kw for kw in MENTAL_STATES if re.search(rf"\b{re.escape(kw)}\b", lowered)
        ]
        theories = [
            kw for kw in THEORY_KEYWORDS if re.search(rf"\b{re.escape(kw)}\b", lowered)
        ]
        cognitive = [
            kw for kw in COGNITIVE_TERMS if re.search(rf"\b{re.escape(kw)}\b", lowered)
        ]
        behavioral = [
            kw for kw in BEHAVIORAL_TERMS if re.search(rf"\b{re.escape(kw)}\b", lowered)
        ]

        if mental_states:
            record.update(
                {"subtype": "mental_state", "states": mental_states, "confidence": 0.7}
            )
        elif theories:
            record.update({"subtype": "theory", "theories": theories, "confidence": 0.6})
        elif cognitive:
            record.update(
                {"subtype": "cognitive_term", "terms": cognitive, "confidence": 0.6}
            )
        elif behavioral:
            record.update(
                {"subtype": "behavioral_term", "terms": behavioral, "confidence": 0.6}
            )
        else:
            record.update({"subtype": "other", "confidence": 0.1})

        results.append(record)

    return results


__all__ = ["parse_psychology_text"]
