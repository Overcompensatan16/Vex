"""Simple regex-based statistics parser.

Extracts statistical statements such as distributions, laws,

and test names from text and converts them into structured

fact dictionaries. Keeps logic lightweight."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List

# Named statistical distributions to recognise
DISTRIBUTIONS = [
    "normal distribution",
    "binomial distribution",
    "poisson distribution",
    "uniform distribution",
    "exponential distribution",
]

# Statistical laws of interest
STAT_LAWS = [
    "law of large numbers",
    "central limit theorem",
]

# Common statistical test names
STAT_TESTS = [
    "t-test",
    "chi-square test",
    "anova",
    "f-test",
    "z-test",
]

# Pattern for sentences like "Bayes theorem states ..."
BAYES_RE = re.compile(r"\bbayes'? theorem states\s+([^.!?]+)", re.IGNORECASE)


def parse_stats_text(text: str) -> List[Dict]:
    """Parse text and return structured statistics fact dictionaries."""
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "statistics",
            "source": "stats_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        lowered = sent.lower()

        bayes_match = BAYES_RE.search(sent)
        if bayes_match:
            record.update(
                {
                    "subtype": "bayes_theorem",
                    "statement": bayes_match.group(1).strip(),
                    "confidence": 0.95,
                }
            )
            results.append(record)
            continue

        law_match = next((law for law in STAT_LAWS if law in lowered), None)
        if law_match:
            record.update(
                {
                    "subtype": "stat_law",
                    "law": law_match,
                    "confidence": 0.9,
                }
            )
        else:
            dist_match = next((dist for dist in DISTRIBUTIONS if dist in lowered), None)
            if dist_match:
                record.update(
                    {
                        "subtype": "distribution",
                        "distribution": dist_match,
                        "confidence": 0.85,
                    }
                )
            else:
                test_match = next((test for test in STAT_TESTS if test in lowered), None)
                if test_match:
                    record.update(
                        {
                            "subtype": "stat_test",
                            "test": test_match,
                            "confidence": 0.8,
                        }
                    )
                else:
                    record.update({"subtype": "other", "confidence": 0.1})

        results.append(record)

    return results


__all__ = ["parse_stats_text"]
