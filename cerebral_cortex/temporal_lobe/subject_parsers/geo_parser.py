"""Simple regex-based geography parser.

This module extracts geographic entities and relations from text,
including rivers, borders, and basic location statements.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List

# Regular expression patterns
LOCATION_RE = re.compile(
    r"\b([A-Z][a-zA-Z ]+?) is located in ([A-Z][a-zA-Z ]+)\b", re.IGNORECASE
)
RIVER_RE = re.compile(r"\b(?:The )?([A-Z][a-zA-Z ]+) River\b", re.IGNORECASE)
BORDER_RE = re.compile(
    r"\b([A-Z][a-zA-Z ]+) borders ([A-Z][a-zA-Z ]+)\b", re.IGNORECASE
)
BORDER_BETWEEN_RE = re.compile(
    r"forms the border between ([A-Z][a-zA-Z ]+) and ([A-Z][a-zA-Z ]+)",
    re.IGNORECASE,
)

def parse_geo_text(text: str) -> List[Dict]:
    """Parse text and return structured geography fact dictionaries."""
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "geography",
            "source": "geo_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        location_match = LOCATION_RE.search(sent)
        river_matches = RIVER_RE.findall(sent)
        border_match = BORDER_RE.search(sent)
        border_between_match = BORDER_BETWEEN_RE.search(sent)

        if location_match:
            record.update(
                {
                    "subtype": "location",
                    "entity": location_match.group(1).strip(),
                    "location": location_match.group(2).strip(),
                    "confidence": 0.9,
                }
            )
        elif river_matches:
            record.update(
                {
                    "subtype": "river",
                    "rivers": [r.strip() for r in river_matches],
                    "confidence": 0.8,
                }
            )
        elif border_match:
            record.update(
                {
                    "subtype": "border",
                    "entities": [
                        border_match.group(1).strip(),
                        border_match.group(2).strip(),
                    ],
                    "confidence": 0.75,
                }
            )
        elif border_between_match:
            record.update(
                {
                    "subtype": "border",
                    "entities": [
                        border_between_match.group(1).strip(),
                        border_between_match.group(2).strip(),
                    ],
                    "confidence": 0.75,
                }
            )

        results.append(record)

    return results


__all__ = ["parse_geo_text"]
