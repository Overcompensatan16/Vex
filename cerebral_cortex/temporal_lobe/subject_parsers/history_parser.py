"""Simple regex-based history parser.

This module extracts basic historical information from text and converts
it into structured fact dictionaries. The focus is on lightweight
patterns like events, timelines, leaders, and dates.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List

# Regular expressions for historical constructs
EVENT_RE = re.compile(r"(.+?)\s+occurred in\s+([^.,;]+)", re.IGNORECASE)
TIMELINE_RE = re.compile(r"from\s+(\d{3,4})\s+(?:to|through|-|until)\s+(\d{3,4})", re.IGNORECASE)
LEADER_RE = re.compile(r"(?:led by|leader(?:\s+is|\s+was)?)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)")
DATE_RE = re.compile(r"\b(\d{3,4})\b")


def parse_history_text(text: str) -> List[Dict]:
    """Parse text and return structured history fact dictionaries."""
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "history",
            "source": "history_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        event_match = EVENT_RE.search(sent)
        if event_match:
            event = event_match.group(1).strip()
            when = event_match.group(2).strip()
            record.update(
                {
                    "subtype": "event",
                    "event": event,
                    "when": when,
                    "confidence": 0.9,
                }
            )
            if DATE_RE.fullmatch(when):
                record["date"] = when
            results.append(record)
            continue

        timeline_match = TIMELINE_RE.search(sent)
        if timeline_match:
            start, end = timeline_match.groups()
            record.update(
                {
                    "subtype": "timeline",
                    "start": start,
                    "end": end,
                    "confidence": 0.8,
                }
            )
            results.append(record)
            continue

        leader_match = LEADER_RE.search(sent)
        if leader_match:
            leader = leader_match.group(1).strip()
            record.update(
                {
                    "subtype": "leader",
                    "leader": leader,
                    "confidence": 0.7,
                }
            )
            results.append(record)
            continue

        date_match = DATE_RE.search(sent)
        if date_match:
            record.update(
                {
                    "subtype": "date",
                    "date": date_match.group(1),
                    "confidence": 0.5,
                }
            )
        else:
            record.update({"subtype": "other", "confidence": 0.1})

        results.append(record)

    return results


__all__ = ["parse_history_text"]