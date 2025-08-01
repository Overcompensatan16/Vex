from datetime import datetime, timezone
from typing import List, Dict
import re
from cerebral_cortex.temporal_lobe.chemistry_parser import parse_chemistry_text

OPINION_MARKERS = [
    "i think",
    "maybe",
    "perhaps",
    "probably",
    "i guess",
]

MATH_SYMBOL_RE = re.compile(r"[=±×÷√∑∏∫∆ΔπσΩθ]")
SCIENCE_KEYWORDS = re.compile(r"\b(energy|force|velocity|mass|quantum|physics)\b", re.IGNORECASE)

HARD_CHEM_PATTERNS = [
    r"^C\d+H\d+",
    r"\bNMR\b|\bIR\b|\bMS\b",
    r"\bstoichiometry\b",
    r"reaction mechanism",
    r"bond angles of",
    r"orbital hybridization",
    r"\borganic synthesis\b",
]


def is_opinion(text: str) -> bool:
    """Very naive check for opinion-like phrases."""
    return any(marker in text.lower() for marker in OPINION_MARKERS)


def _is_hard_chem(text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in HARD_CHEM_PATTERNS)


def generate_from_language(text: str, source: str = "language", analysis: List[str] = None) -> Dict:
    """Generate a base fact record from a sentence."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "type": "opinion" if is_opinion(text) else "fact",
        "subject": None,
        "predicate": None,
        "value": text,
        "conditions": analysis or [],
        "confidence": 0.85 if is_opinion(text) else 1.0,
        "tags": [],
    }


def generate_facts(text: str, source: str = "language") -> List[Dict]:
    """Split text into sentences, tag, and create fact records."""
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    records: List[Dict] = []

    for sent in sentences:
        tags: List[str] = []
        if _is_hard_chem(sent):
            tags.append("chemistry")
            tags.append("hard_chemistry")
        if "chemical" in sent.lower() and "equation" in sent.lower():
            tags.append("physics_related_chemistry")
        if MATH_SYMBOL_RE.search(sent):
            tags.append("math")
        if SCIENCE_KEYWORDS.search(sent):
            tags.append("science")

        rec = generate_from_language(sent, source=source)
        rec["tags"].extend(tags)
        records.append(rec)

        # include structured chemistry facts
        for chem_fact in parse_chemistry_text(sent):
            chem_fact.setdefault("tags", []).append("chemistry")
            records.append(chem_fact)

    return records


def records_from_screen_reasoning(reasoned_screen: Dict) -> List[Dict]:
    """Convert ``reason_over_screen`` output into memory records."""
    records: List[Dict] = []
    for item in reasoned_screen.get("screen_analysis", []):
        text = item.get("original", "")
        analysis = item.get("analysis", [])
        if text:
            records.append(generate_from_language(text, source="ocr_reasoner", analysis=analysis))
    return records
