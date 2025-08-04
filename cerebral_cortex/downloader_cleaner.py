"""Central pipeline to download, clean, and store external knowledge."""

import json
from typing import List, Dict

from external_loaders.wiki_handler import download_and_clean as wiki_download_and_clean
from external_loaders.arxiv_handler import fetch_subject
from cerebral_cortex.fact_generator import generate_facts
from memory_router import store_facts
from external_loaders.download_utils import download_from_manifest


HANDLER_MAP = {
    "wiki": lambda info: wiki_download_and_clean("enwiki", ["Earth", "Moon"], domain="culture"),
    "arxiv": lambda info: fetch_subject("physics"),
}


def run_pipeline(manifest_path: str = "external_loaders/download_manifest.json") -> None:
    """Download sources defined in the manifest and store generated facts."""
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except FileNotFoundError:
        manifest = {}

    # allow other generic downloads for audit/logging
    if manifest:
        download_from_manifest(manifest_path)

    results: List[str] = []
    for key, info in manifest.items():
        if not info.get("enabled", True):
            continue
        handler = HANDLER_MAP.get(key)
        if not handler:
            continue
        results.extend(handler(info))

    for block in results:
        facts = generate_facts(block)


if __name__ == "__main__":
    run_pipeline()
