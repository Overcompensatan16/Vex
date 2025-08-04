"""Simple regex-based biology parser.

This module extracts basic biological information from text
and converts it into structured fact dictionaries. It focuses on
recognizing biological structures, processes, and systems through
keyword lists and simple relational patterns such as "X regulates Y".
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Keyword lists for biological concepts
STRUCTURE_KEYWORDS = {
    "cell",
    "tissue",
    "organ",
    "nucleus",
    "membrane",
    "mitochondria",
    "chloroplast",
}

PROCESS_KEYWORDS = {
    "metabolism",
    "respiration",
    "photosynthesis",
    "replication",
    "transcription",
    "translation",
    "growth",
}

SYSTEM_KEYWORDS = {
    "nervous system",
    "digestive system",
    "circulatory system",
    "immune system",
    "respiratory system",
    "endocrine system",
    "muscular system",
}

# Pattern for simple regulation relationships ("X regulates Y")
REGULATION_RE = re.compile(
    r"\b([A-Za-z\s]+?)\s+(regulates|controls|inhibits|stimulates|activates)\s+([A-Za-z\s]+?)\b",
    re.IGNORECASE,
)


def parse_bio_text(text: str, source_file: Optional[str] = None) -> List[Dict]:
    """Parse text and return structured biology fact dictionaries.

    Parameters
    ----------
    text: str
        Input text containing biology information.
    source_file: Optional[str]
        Optional source filename for context or auditing.
    """
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "biology",
            "source": "bio_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        lowered = sent.lower()

        # Check for regulation relationships
        reg_match = REGULATION_RE.search(sent)
        if reg_match:
            subject = reg_match.group(1).strip()
            verb = reg_match.group(2).lower()
            obj = reg_match.group(3).strip()
            record.update(
                {
                    "subtype": "regulation",
                    "subject": subject,
                    "verb": verb,
                    "object": obj,
                    "confidence": 0.9,
                }
            )
            results.append(record)
            continue

        structures = [
            kw for kw in STRUCTURE_KEYWORDS if re.search(rf"\b{re.escape(kw)}\b", lowered)
        ]
        processes = [
            kw for kw in PROCESS_KEYWORDS if re.search(rf"\b{re.escape(kw)}\b", lowered)
        ]
        systems = [
            kw for kw in SYSTEM_KEYWORDS if re.search(rf"\b{re.escape(kw)}\b", lowered)
        ]

        if structures:
            record.update(
                {"subtype": "structure", "structures": structures, "confidence": 0.7}
            )
        elif processes:
            record.update(
                {"subtype": "process", "processes": processes, "confidence": 0.6}
            )
        elif systems:
            record.update(
                {"subtype": "system", "systems": systems, "confidence": 0.6}
            )
        else:
            record.update({"subtype": "other", "confidence": 0.1})

        results.append(record)

    return results


__all__ = ["parse_bio_text"]
