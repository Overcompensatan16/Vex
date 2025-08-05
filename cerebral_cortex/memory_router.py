"""Simple helper to write fact records to category-based memory stores."""

import os
import inspect
from collections import defaultdict
from typing import Iterable, Dict
from hippocampus.fact_router import route_and_write_fact, FactRouter

# ✅ Dynamically support config_path in FactRouter init
CONFIG_PATH = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "hippocampus",
        "memory",
        "fact_memory_config.json",
    )
)
_router_kwargs = {}
if "config_path" in inspect.signature(FactRouter.__init__).parameters:
    _router_kwargs["config_path"] = CONFIG_PATH
_router = FactRouter(**_router_kwargs)


def store_facts(fact_list: Iterable[Dict]) -> Dict[str, Dict[str, int]]:
    """Append each fact dictionary to its appropriate memory file.

    Returns a mapping of destination paths to ``{"stored": int, "skipped": int}``.
    """

    stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"stored": 0, "skipped": 0})
    for fact in fact_list:
        if not isinstance(fact, dict):
            continue
        stored, path = route_and_write_fact(fact)
        if not path:
            # Warning already emitted by helper
            continue
        entry = stats[path]
        if stored:
            entry["stored"] += 1
        else:
            entry["skipped"] += 1

    for path, counts in stats.items():
        print(f"[store_facts] Stored {counts['stored']} facts in {path}")
        if counts["skipped"]:
            print(f"[store_facts] Skipped {counts['skipped']} duplicate facts")

    return stats
