"""Simple regex-based sociology parser.

This module extracts basic sociological information from text
and converts it into structured fact dictionaries. It focuses on
recognizing social institutions, norms, and stratification terms
through keyword lists and simple patterns such as "X is a social
institution that...".
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Keyword lists for sociological concepts
SOCIAL_INSTITUTIONS = {
    "family",
    "education",
    "religion",
    "economy",
    "government",
    "media",
}

NORMS_KEYWORDS = {
    "norm",
    "value",
    "custom",
    "tradition",
    "law",
}

STRATIFICATION_KEYWORDS = {
    "class",
    "status",
    "hierarchy",
    "caste",
    "inequality",
}

# Pattern for social institution definitions ("X is a social institution that ...")
INSTITUTION_DEF_RE = re.compile(
    r"\b([A-Za-z\s]+?)\s+is a social institution that\s+([A-Za-z\s]+?)\b",
    re.IGNORECASE,
)


def parse_sociology_text(text: str, source_file: Optional[str] = None) -> List[Dict]:
    """Parse text and return structured sociology fact dictionaries.

    Parameters
    ----------
    text: str
        Input text containing sociology information.
    source_file: Optional[str]
        Optional source filename for context or auditing.
    """
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "sociology",
            "source": "sociology_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        lowered = sent.lower()

        # Check for social institution definition pattern
        inst_match = INSTITUTION_DEF_RE.search(sent)
        if inst_match:
            institution = inst_match.group(1).strip()
            description = inst_match.group(2).strip()
            record.update(
                {
                    "subtype": "institution_definition",
                    "institution": institution,
                    "description": description,
                    "confidence": 0.9,
                }
            )
            results.append(record)
            continue

        institutions = [
            kw
            for kw in SOCIAL_INSTITUTIONS
            if re.search(rf"\b{re.escape(kw)}\b", lowered)
        ]
        norms = [
            kw for kw in NORMS_KEYWORDS if re.search(rf"\b{re.escape(kw)}\b", lowered)
        ]
        strat_terms = [
            kw
            for kw in STRATIFICATION_KEYWORDS
            if re.search(rf"\b{re.escape(kw)}\b", lowered)
        ]

        if institutions:
            record.update(
                {"subtype": "institution", "institutions": institutions, "confidence": 0.7}
            )
        elif norms:
            record.update({"subtype": "norm", "norms": norms, "confidence": 0.6})
        elif strat_terms:
            record.update(
                {
                    "subtype": "stratification",
                    "terms": strat_terms,
                    "confidence": 0.6,
                }
            )
        else:
            record.update({"subtype": "other", "confidence": 0.1})

        results.append(record)

    return results


__all__ = ["parse_sociology_text"]
