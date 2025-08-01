import os
from typing import List, Dict

from cerebral_cortex.source_handlers.external_loaders.wiki_handler import parse_dump as parse_wiki
from cerebral_cortex.source_handlers.external_loaders.factbook_handler import parse_dump as parse_factbook
from cerebral_cortex.source_handlers.external_loaders.arxiv_handler import parse_dump as parse_arxiv
from cerebral_cortex.fact_generator import generate_facts
from cerebral_cortex.memory_router import store_facts


SOURCE_MAP = {
    "wiki": parse_wiki,
    "factbook": parse_factbook,
    "arxiv": parse_arxiv,
}


def process_batch(records: List[Dict]) -> None:
    """Parse downloaded dumps and route generated facts."""
    for rec in records:
        path = rec.get("path")
        if not path or not os.path.exists(path):
            continue
        source = rec.get("source")
        parser = SOURCE_MAP.get(source)
        if not parser:
            continue
        blocks = parser(path)
        for block in blocks:
            facts = generate_facts(block, source=source)
            store_facts(facts)
