"""Simple parser for conservation-related text.

This module detects conservation organizations, species statuses,
and treaties from plain text and provides lightweight named entity
recognition patterns for wildlife terms and organizations.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List

# Known conservation organizations
CONSERVATION_ORGS = [
    "World Wildlife Fund",
    "International Union for Conservation of Nature",
    "Wildlife Conservation Society",
    "Conservation International",
    "The Nature Conservancy",
]

# Species conservation statuses
SPECIES_STATUSES = [
    "critically endangered",
    "endangered",
    "vulnerable",
    "near threatened",
    "least concern",
    "extinct",
]

# International conservation treaties
TREATIES = [
    "CITES",  # Convention on International Trade in Endangered Species
    "Endangered Species Act",
    "Convention on Biological Diversity",
    "Ramsar Convention",
]

# NER patterns for wildlife terms and organizations
NER_WILDLIFE_PATTERNS = [
    {"label": "WILDLIFE", "pattern": "habitat"},
    {"label": "WILDLIFE", "pattern": "biodiversity"},
    {"label": "WILDLIFE", "pattern": "ecosystem"},
    {"label": "WILDLIFE", "pattern": "poaching"},
    {"label": "WILDLIFE", "pattern": "sanctuary"},
]

NER_ORG_PATTERNS = [{"label": "ORG", "pattern": org} for org in CONSERVATION_ORGS]

NER_PATTERNS = NER_WILDLIFE_PATTERNS + NER_ORG_PATTERNS


def parse_conservation_text(text: str) -> List[Dict]:
    """Parse text and return structured conservation fact dictionaries."""
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "conservation",
            "source": "conservation_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        lowered = sent.lower()
        org = next((o for o in CONSERVATION_ORGS if o.lower() in lowered), None)
        status = next((s for s in SPECIES_STATUSES if s in lowered), None)
        treaty = next((t for t in TREATIES if t.lower() in lowered), None)

        if org:
            record.update({
                "subtype": "organization",
                "organization": org,
                "confidence": 0.9,
            })
        elif status:
            record.update({
                "subtype": "status",
                "status": status,
                "confidence": 0.8,
            })
        elif treaty:
            record.update({
                "subtype": "treaty",
                "treaty": treaty,
                "confidence": 0.85,
            })
        else:
            wildlife_terms = [
                p["pattern"]
                for p in NER_WILDLIFE_PATTERNS
                if p["pattern"].lower() in lowered
            ]
            if wildlife_terms:
                record.update({
                    "subtype": "term",
                    "terms": wildlife_terms,
                    "confidence": 0.5,
                })
            else:
                record.update({"subtype": "other", "confidence": 0.1})

        results.append(record)

    return results


__all__ = ["parse_conservation_text", "NER_PATTERNS"]
