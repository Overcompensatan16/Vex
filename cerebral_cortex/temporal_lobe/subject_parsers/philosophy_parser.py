"""Simple regex-based philosophy parser.

This module extracts philosophical concepts and philosopher names from text
and converts them into structured fact dictionaries for downstream
processing. It also recognizes definitions such as "X is the study of Y"
and basic hierarchical relationships like "X is a branch of Y".
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List

# Common philosophical concepts of interest
CONCEPTS = [
    "ethics",
    "epistemology",
    "metaphysics",
    "aesthetics",
    "logic",
    "ontology",
    "existentialism",
    "rationalism",
    "empiricism",
    "stoicism",
    "utilitarianism",
    "deontology",
    "phenomenology",
    "pragmatism",
    "dualism",
    "monism",
]

# Well known philosophers for named entity detection
PHILOSOPHERS = [
    "Socrates",
    "Plato",
    "Aristotle",
    "Descartes",
    "Kant",
    "Nietzsche",
    "Hume",
    "Confucius",
    "Locke",
    "Spinoza",
    "Hegel",
]

# Regex patterns for definitional structures
STUDY_OF_RE = re.compile(r"\b([A-Za-z][A-Za-z\s]+?)\s+is\s+the\s+study\s+of\s+([A-Za-z\s]+)\b", re.IGNORECASE)
BRANCH_OF_RE = re.compile(r"\b([A-Za-z][A-Za-z\s]+?)\s+is\s+a\s+branch\s+of\s+([A-Za-z\s]+)\b", re.IGNORECASE)


def parse_philosophy_text(text: str) -> List[Dict]:
    """Parse text and return structured philosophy fact dictionaries."""
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "philosophy",
            "source": "philosophy_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        lowered = sent.lower()

        # Named philosopher detection
        philosopher = next(
            (
                name
                for name in PHILOSOPHERS
                if re.search(rf"\b{re.escape(name)}\b", sent, re.IGNORECASE)
            ),
            None,
        )
        if philosopher:
            record.update({
                "subtype": "philosopher",
                "name": philosopher,
                "confidence": 0.9,
            })
            results.append(record)
            continue

        # Definitions: "X is the study of Y"
        match = STUDY_OF_RE.search(sent)
        if match:
            field, subject = match.group(1).strip(), match.group(2).strip()
            record.update({
                "subtype": "study_of",
                "field": field,
                "subject": subject,
                "confidence": 0.85,
            })
            results.append(record)
            continue

        # Hierarchical relation: "X is a branch of Y"
        match = BRANCH_OF_RE.search(sent)
        if match:
            branch, field = match.group(1).strip(), match.group(2).strip()
            record.update({
                "subtype": "branch_of",
                "branch": branch,
                "field": field,
                "confidence": 0.8,
            })
            results.append(record)
            continue

        # Concept detection
        concepts = [c for c in CONCEPTS if re.search(rf"\b{re.escape(c)}\b", lowered)]
        if concepts:
            record.update({
                "subtype": "concept",
                "concepts": concepts,
                "confidence": 0.6,
            })
        else:
            record.update({"subtype": "other", "confidence": 0.1})

        results.append(record)

    return results


__all__ = ["parse_philosophy_text"]
