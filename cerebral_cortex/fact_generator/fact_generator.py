from datetime import datetime, timezone
from typing import List, Dict
import re

try:  # mapping arXiv category codes to internal types
    from cerebral_cortex.source_handlers.external_loaders.arxiv_handler import CODE_TO_TYPE
except Exception:  # pragma: no cover - arxiv handler optional in some envs
    CODE_TO_TYPE = {}

from cerebral_cortex.temporal_lobe.chemistry_parser import parse_chemistry_text
from cerebral_cortex.source_handlers.transformer_fact_extractor import transform_text

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
        "subject": "",
        "predicate": "",
        "value": text,
        "conditions": analysis or [],
        "confidence": 0.85 if is_opinion(text) else 1.0,
        "tags": [],
    }


def generate_facts(
    text: str, source: str = "language", source_type: str | None = None
) -> List[Dict]:
    """Split ``text`` into sentence-level fact records.

    Parameters
    ----------
    text:
        Already-parsed text to split and analyse.  The input is first passed
        through :func:`transform_text` to normalise it for downstream
        processing.
    source:
        Originating source label (``"language"`` by default).
    source_type:
        Optional subtype supplied by upstream loaders.  For arXiv sources this
        should be the arXiv category code (e.g. ``"cs.AI"``) which is mapped to
        our internal ``type`` using :data:`CODE_TO_TYPE`.  For Wikipedia the
        caller may provide an already classified topic string (e.g.
        ``"history.rome"``).
    """

    text = transform_text(text)
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

        if source_type:
            if source == "arxiv":
                rec["type"] = CODE_TO_TYPE.get(source_type, source_type)
            elif source in {"wiki", "wikipedia"}:
                rec["type"] = source_type

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
            transformed = transform_text(text)
            print(
                "Transformer normalization applied to OCR/STT input",
                {"tag": "ocr", "source": "ocr_reasoner"},
            )
            records.append(
                generate_from_language(
                    transformed, source="ocr_reasoner", analysis=analysis
                )
            )
    return records
