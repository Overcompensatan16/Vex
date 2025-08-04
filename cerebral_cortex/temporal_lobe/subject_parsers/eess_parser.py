"""Simple regex-based electrical engineering and signal processing parser.

This module extracts basic EESS information from text and converts it into
structured fact dictionaries suitable for downstream processing. It focuses on
recognizing circuit components, signal processing concepts, and hardware
references. It also captures amplification patterns of the form "X amplifies Y".
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Keyword lists for different electrical engineering domains
CIRCUIT_KEYWORDS = {
    "resistor",
    "capacitor",
    "inductor",
    "transistor",
    "diode",
    "op-amp",
    "op amp",
    "circuit",
}

SIGNAL_KEYWORDS = {
    "filter",
    "fourier",
    "fft",
    "dft",
    "sampling",
    "convolution",
    "signal",
    "frequency",
    "noise",
}

HARDWARE_KEYWORDS = {
    "cpu",
    "gpu",
    "fpga",
    "microcontroller",
    "asic",
    "board",
    "pcb",
    "chip",
    "integrated circuit",
    "ic",
}

# Pattern capturing "X amplifies Y"
AMPLIFICATION_RE = re.compile(
    r"\b(?P<amp>[\w\s-]+?)\s+amplifies\s+(?P<target>[\w\s-]+)", re.IGNORECASE
)


def parse_eess_text(text: str, source_file: Optional[str] = None) -> List[Dict]:
    """Parse text and return structured EESS fact dictionaries.

    Parameters
    ----------
    text: str
        Input text containing electrical engineering information.
    source_file: Optional[str]
        Optional source filename for context or auditing.
    """
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "eess",
            "source": "eess_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        lowered = sent.lower()

        amp_match = AMPLIFICATION_RE.search(sent)
        if amp_match:
            record.update(
                {
                    "subtype": "amplification",
                    "amplifier": amp_match.group("amp").strip(),
                    "target": amp_match.group("target").strip(),
                    "confidence": 0.9,
                }
            )
            results.append(record)
            continue

        circuit_matches = [kw for kw in CIRCUIT_KEYWORDS if kw in lowered]
        signal_matches = [kw for kw in SIGNAL_KEYWORDS if kw in lowered]
        hardware_matches = [kw for kw in HARDWARE_KEYWORDS if kw in lowered]

        if circuit_matches:
            record.update(
                {
                    "subtype": "circuit",
                    "keywords": circuit_matches,
                    "confidence": 0.7,
                }
            )
        elif signal_matches:
            record.update(
                {
                    "subtype": "signal_processing",
                    "keywords": signal_matches,
                    "confidence": 0.6,
                }
            )
        elif hardware_matches:
            record.update(
                {
                    "subtype": "hardware",
                    "keywords": hardware_matches,
                    "confidence": 0.6,
                }
            )
        else:
            record.update({"subtype": "other", "confidence": 0.1})

        results.append(record)

    return results


__all__ = ["parse_eess_text"]
