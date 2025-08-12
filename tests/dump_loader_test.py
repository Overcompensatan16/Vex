"""Unified dump pipeline harness for wiki and arXiv sources.

This script exercises the download, preprocessing, and routing modules
using local sample dumps. It replaces the previous ad-hoc wiki/arxiv
tests with a single harness that runs a couple of batches through the
full pipeline while routing facts into the existing test memory store.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Iterable, List

# Ensure repository root on path for module imports
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Lightweight stubs for optional heavy dependencies
import types
if "spacy" not in sys.modules:
    sys.modules["spacy"] = types.SimpleNamespace(load=lambda name: None)
    sys.modules["spacy"].cli = types.SimpleNamespace(download=lambda name: None)
sys.modules.setdefault("pygetwindow", types.ModuleType("pygetwindow"))
sys.modules.setdefault("pyautogui", types.ModuleType("pyautogui"))
temporal_stub = types.ModuleType("cerebral_cortex.temporal_lobe")
chemistry_stub = types.ModuleType("cerebral_cortex.temporal_lobe.chemistry_parser")
chemistry_stub.parse_chemistry_text = lambda text: []
temporal_stub.chemistry_parser = chemistry_stub
temporal_stub.__path__ = []
sys.modules.setdefault("cerebral_cortex.temporal_lobe", temporal_stub)
sys.modules.setdefault("cerebral_cortex.temporal_lobe.chemistry_parser", chemistry_stub)

from mock_memory_router import MockMemoryRouter, TEST_MEMORY_PATH

import cerebral_cortex.source_handlers.external_loaders.batch_scheduler as sched
from cerebral_cortex.source_handlers.download_utils import download_files
from cerebral_cortex.source_handlers.external_loaders.preprocessor import process_batch
import cerebral_cortex.memory_router as memory_router
import cerebral_cortex.source_handlers.external_loaders.preprocessor as preprocessor


# --- Patch memory router to use the test memory store -----------------

_mock_router = MockMemoryRouter()


def _mock_store_facts(facts: Iterable[Dict]) -> Dict[str, Dict[str, int]]:
    """Route ``facts`` through ``MockMemoryRouter`` and collect stats."""

    stats: Dict[str, Dict[str, int]] = {}
    for fact in facts:
        record = {
            "subject": fact.get("subject", "unknown"),
            "predicate": fact.get("predicate", "states"),
            "value": fact.get("value") or fact.get("fact", ""),
            "category": fact.get("source", "general"),
        }
        stored = _mock_router.route(record)
        path = os.path.join(TEST_MEMORY_PATH, f"{record['category'].replace('/', '_')}.jsonl")
        entry = stats.setdefault(path, {"stored": 0, "skipped": 0})
        if stored:
            entry["stored"] += 1
        else:
            entry["skipped"] += 1
    return stats


memory_router.store_facts = _mock_store_facts  # type: ignore
preprocessor.store_facts = _mock_store_facts  # type: ignore


def _memory_count() -> int:
    """Return total number of records written to the mock memory store."""

    total = 0
    base = Path(TEST_MEMORY_PATH)
    for path in base.glob("*.jsonl"):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                total += sum(1 for _ in fh)
        except OSError:
            pass
    return total


# --- Helpers -----------------------------------------------------------


def _create_sample_dumps(base: Path) -> List[Dict]:
    """Write minimal wiki and arXiv dumps under ``base`` and return records."""

    arxiv_xml = """<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns='http://www.w3.org/2005/Atom'>
  <entry>
    <title>Sample Paper</title>
    <summary>This is a test summary about AI.</summary>
    <category term='cs.AI'/>
  </entry>
</feed>
"""

    wiki_text = "== Heading ==\n\nThis is a sample paragraph from wikipedia.\nAnother sentence."

    arxiv_path = base / "arxiv_sample.xml"
    wiki_path = base / "wiki_sample.txt"
    arxiv_path.write_text(arxiv_xml, encoding="utf-8")
    wiki_path.write_text(wiki_text, encoding="utf-8")

    return [
        {
            "id": "wiki_1",
            "name": "Wiki Sample",
            "url": wiki_path.as_uri(),
            "source": "wiki",
        },
        {
            "id": "arxiv_1",
            "name": "arXiv Sample",
            "url": arxiv_path.as_uri(),
            "source": "arxiv",
            "subject": "cs.AI",
        },
        {
            "id": "wiki_2",
            "name": "Wiki Sample 2",
            "url": wiki_path.as_uri(),
            "source": "wiki",
        },
    ]


# --- Main harness ------------------------------------------------------


def main() -> None:
    """Run the pipeline on a couple of batches of sample data."""

    with TemporaryDirectory() as src_dir, TemporaryDirectory() as dump_dir:
        src_base = Path(src_dir)
        dump_base = Path(dump_dir)

        records = _create_sample_dumps(src_base)

        # Partition into batches using scheduler helper
        batches = [
            (i, i + len(b), b) for i, b in enumerate(sched._partition(records, 1))
        ]

        for start, end, batch in batches:
            downloaded = download_files(batch, dump_base=str(dump_base))
            result = process_batch(downloaded, dump_base=str(dump_base))
            print(f"Batch {start}-{end}: {result}")

        print(f"Total facts stored: {_memory_count()}")


if __name__ == "__main__":
    main()
