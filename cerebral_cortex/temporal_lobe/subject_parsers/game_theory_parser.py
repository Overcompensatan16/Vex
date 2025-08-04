"""Simple regex-based game theory parser.

This module extracts game theory related information such as strategies,
known game names, equilibria, and payoff matrices from text and converts
it into structured fact dictionaries. The logic intentionally remains
lightweight and heuristic based."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List

# Named standard games for basic NER
STANDARD_GAMES: Dict[str, str] = {
    "prisoner's dilemma": "classic cooperation vs. defection game",
    "battle of the sexes": "coordination game with different preferences",
    "stag hunt": "coordination game with safety vs. social cooperation",
    "hawk-dove": "conflict game also known as chicken",
    "chicken": "anti-coordination game of brinkmanship",
    "ultimatum game": "bargaining game involving fairness",
    "dictator game": "allocation game with unilateral control",
    "public goods game": "cooperation game with shared resources",
    "cournot competition": "duopoly model with quantity setting",
    "bertrand competition": "duopoly model with price setting",
}

# Regex patterns for strategies, equilibria, and payoff matrices
STRATEGY_RE = re.compile(
    r"\b(dominant strategy|mixed strategy|pure strategy|strategy|strategies)\b",
    re.IGNORECASE,
)
EQUILIBRIUM_RE = re.compile(
    r"\b(nash equilibrium|equilibrium|equilibria|pareto(?:\s+optimal)?)\b",
    re.IGNORECASE,
)
# Detect simple 2x2 matrix representations like "[[1, 2], [3, 4]]" or mentions
PAYOFF_MATRIX_RE = re.compile(r"\[\s*\[[^]]+]\s*,\s*\[[^]]+]\s*]")


def parse_game_theory_text(text: str) -> List[Dict]:
    """Parse text and return structured game theory fact dictionaries."""
    results: List[Dict] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    for sent in sentences:
        record: Dict = {
            "type": "game_theory",
            "source": "game_theory_parser",
            "fact": sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        lowered = sent.lower()

        # Named games
        game_match = next((g for g in STANDARD_GAMES if g in lowered), None)
        if game_match:
            record.update(
                {
                    "subtype": "game",
                    "name": game_match,
                    "description": STANDARD_GAMES[game_match],
                    "confidence": 0.9,
                }
            )
        elif PAYOFF_MATRIX_RE.search(sent) or "payoff matrix" in lowered:
            matrix = PAYOFF_MATRIX_RE.search(sent)
            record.update(
                {
                    "subtype": "payoff_matrix",
                    "matrix": matrix.group(0) if matrix else "payoff matrix",
                    "confidence": 0.85 if matrix else 0.75,
                }
            )
        elif EQUILIBRIUM_RE.search(sent):
            eq = EQUILIBRIUM_RE.search(sent).group(0)
            record.update(
                {
                    "subtype": "equilibrium",
                    "equilibrium": eq,
                    "confidence": 0.8,
                }
            )
        elif STRATEGY_RE.search(sent):
            strategies = [s.lower() for s in STRATEGY_RE.findall(sent)]
            record.update(
                {
                    "subtype": "strategy",
                    "strategies": strategies,
                    "confidence": 0.6,
                }
            )

        results.append(record)

    return results


__all__ = ["parse_game_theory_text"]
