"""Simple regex-based law parser.

This module extracts legal references such as constitutional clauses,
court decisions, and legislative acts from text and converts them into
structured fact dictionaries for downstream processing.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List

# Pattern for constitutional clauses like "The First Amendment guarantees ..."
CONSTITUTIONAL_CLAUSE_RE = re.compile(
    r"\bThe\s+(?P<amendment>[A-Za-z]+\s+Amendment)\s+(?:guarantees|protects|ensures)\s+(?P<right>[^.]+)",
    re.IGNORECASE,
)

# Pattern for court decisions like "Brown v. Board of Education"
COURT_DECISION_RE = re.compile(
    r"\b([A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*)\s+(?:v\.|vs\.)\s+([A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*)\b(?:\s*\(\d{4}\))?",
)

# Pattern for acts like "Civil Rights Act of 1964"
ACT_RE = re.compile(
    r"\b([A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*\s+Act(?:\s+of\s+\d{4})?)",
)


def parse_law_text(text: str) -> List[Dict]:
    """Parse text and return structured law fact dictionaries."""
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "law",
            "source": "law_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        clause_match = CONSTITUTIONAL_CLAUSE_RE.search(sent)
        if clause_match:
            record.update(
                {
                    "subtype": "constitutional_clause",
                    "clause": clause_match.group("amendment").strip(),
                    "guarantee": clause_match.group("right").strip(),
                    "confidence": 0.9,
                }
            )
            results.append(record)
            continue

        court_match = COURT_DECISION_RE.search(sent)
        if court_match:
            case = f"{court_match.group(1)} v. {court_match.group(2)}"
            record.update(
                {
                    "subtype": "court_decision",
                    "case": case,
                    "confidence": 0.85,
                }
            )
            results.append(record)
            continue

        act_match = ACT_RE.search(sent)
        if act_match:
            record.update(
                {
                    "subtype": "act",
                    "act": act_match.group(1).strip(),
                    "confidence": 0.8,
                }
            )
            results.append(record)
            continue

        record.update({"subtype": "other", "confidence": 0.1})
        results.append(record)

    return results


__all__ = ["parse_law_text"]
