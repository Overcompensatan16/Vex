import re
from typing import Optional


def parse_fact_from_sentence(sentence: str) -> dict:
    """
    Parses a natural language sentence into a symbolic fact dictionary.
    Returns subject, predicate, value, confidence, and source.
    """
    sentence = sentence.strip()

    # Common 'is' pattern
    match = re.match(r"(?:Did you know|It's known that)?\s*(.+?)\s+is\s+(.+?)[?.!]?$", sentence, re.IGNORECASE)
    if match:
        subject, value = match.groups()
        return {
            "subject": subject.strip(),
            "predicate": "is",
            "value": value.strip(),
            "confidence": 0.85,
            "source": "fact_extractor"
        }

    # Cause pattern
    match = re.match(r"(.+?)\s+causes\s+(.+?)[?.!]?$", sentence, re.IGNORECASE)
    if match:
        subject, value = match.groups()
        return {
            "subject": subject.strip(),
            "predicate": "causes",
            "value": value.strip(),
            "confidence": 0.85,
            "source": "fact_extractor"
        }

    # Needs/depends on pattern
    match = re.match(r"(.+?)\s+(?:needs|depends on)\s+(.+?)[?.!]?$", sentence, re.IGNORECASE)
    if match:
        subject, value = match.groups()
        return {
            "subject": subject.strip(),
            "predicate": "depends_on",
            "value": value.strip(),
            "confidence": 0.8,
            "source": "fact_extractor"
        }

    # Fallback case
    return {
        "subject": "unknown",
        "predicate": "says",
        "value": sentence,
        "confidence": 0.5,
        "source": "fact_extractor"
    }
