"""Simple regex-based environmental science parser.

This module extracts basic environmental information from text and converts
it into structured fact dictionaries. The goal is to recognise high level
ecological processes (e.g. the carbon cycle) and references to common
environmental legislation without attempting deep scientific reasoning.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

# General environment related keywords for loose topical detection
ENVIRONMENT_KEYWORDS = [
    "ecosystem",
    "habitat",
    "biodiversity",
    "conservation",
    "sustainability",
    "pollution",
    "recycle",
    "deforestation",
    "emissions",
    "climate",
    "renewable",
    "wildlife",
    "soil",
    "water quality",
    "air quality",
    "biosphere",
]

# Named environmental laws or agreements of interest
ENVIRONMENT_LAWS = [
    "Clean Air Act",
    "Clean Water Act",
    "Endangered Species Act",
    "National Environmental Policy Act",
    "Paris Agreement",
    "Kyoto Protocol",
]

# Recognised ecological processes or interactions
ENVIRONMENT_PROCESSES = [
    "carbon cycle",
    "nitrogen cycle",
    "water cycle",
    "photosynthesis",
    "respiration",
    "decomposition",
    "food chain",
    "food web",
    "symbiosis",
    "mutualism",
    "commensalism",
    "parasitism",
    "predation",
    "competition",
]


def parse_environment_text(text: str, source_file: Optional[str] = None) -> List[Dict]:
    """Parse text and return structured environmental fact dictionaries."""

    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "environment",
            "source": "environment_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        lowered = sent.lower()

        # Named environmental laws or agreements
        law_match = next(
            (law for law in ENVIRONMENT_LAWS if law.lower() in lowered), None
        )
        if law_match:
            record.update({
                "subtype": "law",
                "law": law_match,
                "confidence": 0.9,
            })
            results.append(record)
            continue

        # Ecological processes and biosphere interactions
        process_match = next(
            (proc for proc in ENVIRONMENT_PROCESSES if proc in lowered), None
        )
        if process_match:
            record.update({
                "subtype": "process",
                "process": process_match,
                "confidence": 0.8,
            })
            results.append(record)
            continue

        # General keywords
        keywords = [
            kw
            for kw in ENVIRONMENT_KEYWORDS
            if re.search(rf"\b{re.escape(kw)}\b", lowered)
        ]
        if keywords:
            record.update({
                "subtype": "keyword",
                "keywords": keywords,
                "confidence": 0.5,
            })
        else:
            record.update({"subtype": "other", "confidence": 0.1})

        results.append(record)

    return results


__all__ = ["parse_environment_text"]
