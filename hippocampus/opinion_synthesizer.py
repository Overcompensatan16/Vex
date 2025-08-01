import json
import os
from typing import List, Dict, Iterable, Optional
from hippocampus.fact_router import FactRouter


class OpinionSynthesizer:
    """Aggregate routed facts into a simple synthesized opinion."""

    def __init__(self, router: Optional[FactRouter] = None, max_facts: int = 50) -> None:
        self.router = router or FactRouter()
        self.max_facts = max_facts

    def _load_from_categories(self, categories: Iterable[str]) -> List[Dict]:
        records: List[Dict] = []
        for cat in categories:
            for fact in self.router.load_facts(cat):
                records.append(fact)
                if len(records) >= self.max_facts:
                    return records
        return records

    def synthesize_opinion(self, query_tags: Optional[List[str]] = None,
                           categories: Optional[List[str]] = None) -> Dict:
        cats = categories or list(self.router.routes.keys())
        records = self._load_from_categories(cats)
        if query_tags:
            records = [r for r in records if all(t in r.get("tags", []) for t in query_tags)]
        opinion = f"Aggregated {len(records)} facts" if records else "No basis for opinion"
        return {
            "opinion": opinion,
            "basis": records,
            "tags": query_tags or [],
            "confidence": 1.0 if records else 0.0,
        }
