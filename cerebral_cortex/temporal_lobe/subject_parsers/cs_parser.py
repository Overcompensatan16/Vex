"""Simple regex-based computer science parser.

This module extracts basic computer science information from text
and converts it into structured fact dictionaries. It focuses on
recognizing AI-related and cryptographic terms as well as common
algorithm mentions. It also captures descriptive patterns starting
with "A neural network".
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Keyword lists for different CS subdomains
AI_KEYWORDS = {
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "reinforcement learning",
    "natural language processing",
    "nlp",
}

CRYPTO_KEYWORDS = {
    "encryption",
    "decryption",
    "cipher",
    "cryptography",
    "public key",
    "private key",
    "hash",
    "blockchain",
    "rsa",
    "aes",
    "sha-256",
    "digital signature",
}

ALGORITHM_KEYWORDS = {
    "quicksort",
    "merge sort",
    "binary search",
    "dijkstra",
    "bellman-ford",
    "breadth-first search",
    "depth-first search",
    "algorithm",
}

# Pattern capturing sentences starting with "A neural network ..."
NEURAL_NETWORK_RE = re.compile(r"\bA neural network\b[^.?!]*", re.IGNORECASE)


def parse_cs_text(text: str, source_file: Optional[str] = None) -> List[Dict]:
    """Parse text and return structured computer science fact dictionaries.

    Parameters
    ----------
    text: str
        Input text containing computer science information.
    source_file: Optional[str]
        Optional source filename for context or auditing.
    """
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "computer_science",
            "source": "cs_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        lowered = sent.lower()

        neural_match = NEURAL_NETWORK_RE.search(sent)
        if neural_match:
            record.update(
                {
                    "subtype": "neural_network",
                    "description": neural_match.group(0),
                    "confidence": 0.9,
                }
            )
            results.append(record)
            continue

        ai_matches = [kw for kw in AI_KEYWORDS if kw in lowered]
        crypto_matches = [kw for kw in CRYPTO_KEYWORDS if kw in lowered]
        algo_matches = [kw for kw in ALGORITHM_KEYWORDS if kw in lowered]

        if ai_matches:
            record.update(
                {"subtype": "ai", "keywords": ai_matches, "confidence": 0.7}
            )
        elif crypto_matches:
            record.update(
                {"subtype": "cryptography", "keywords": crypto_matches, "confidence": 0.7}
            )
        elif algo_matches:
            record.update(
                {"subtype": "algorithm", "algorithms": algo_matches, "confidence": 0.6}
            )
        else:
            record.update({"subtype": "other", "confidence": 0.1})

        results.append(record)

    return results


__all__ = ["parse_cs_text"]
