"""Simple helper to write fact records to category-based memory stores."""

import os
from typing import Iterable, Dict
from hippocampus.fact_router import FactRouter


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "hippocampus", "memory", "fact_memory_config.json")
_router = FactRouter(CONFIG_PATH)


def store_facts(fact_list: Iterable[Dict]) -> None:
    """Append each fact dictionary to its appropriate memory file."""
    for fact in fact_list:
        if not isinstance(fact, dict):
            continue
        _router.route_fact(fact)
