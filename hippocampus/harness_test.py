import json
import os
import sys
from hippocampus.hippocampus_module import HippocampusModule
from memory.memory_store_factory import MemoryStoreFactory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run_harness():
    factory = MemoryStoreFactory()
    hippocampus = HippocampusModule(
        memory_factory=factory,
        external_memory_path="external_memory.jsonl",
    )

    test_records = [
        {"fact": "Generic general fact", "tags": ["meta_reasoning"]},
        {"fact": "Opinionated insight", "type": "opinion", "tags": ["opinion"]},
        {"fact": "Math conclusion: 2+2=4", "type": "math_conclusion", "tags": ["math"]},
        {"fact": "Emotional expression", "type": "emotion", "tags": ["emotion"]},
        {"fact": "Historical insight", "tags": ["history"]},
        {"fact": "Science insight", "tags": ["science"]},
        {"fact": "Philosophical thought", "tags": ["philosophy"]},
        {"fact": "Tech innovation", "tags": ["technology"]},
        {"fact": "Famous biography", "tags": ["biography"]},
        {"fact": "Geographical fact", "tags": ["geography"]},
        {"fact": "Cultural reference", "tags": ["culture"]},
        {"fact": "E=mc^2 relates mass and energy", "tags": ["physics"]},
        {"fact": "Orbital hybridization in benzene", "tags": ["chemistry"]},
        {"fact": "Fallback to linguistic", "type": "observation", "tags": ["test"]},
    ]

    for record in test_records:
        record.update({
            "tarot": {"trump": None, "suit": "Pentacles"},
            "source": "harness",
            "credibility": 1.0,
        })
        hippocampus.store_record(record)

    results = hippocampus.query_facts(query_tags=["test"])
    print("[Harness] Queried records:")
    for r in results:
        print(json.dumps(r, indent=2))

    print("[Harness] Recent context entries:")
    for c in hippocampus.context.recent():
        print(json.dumps(c, indent=2))


if __name__ == "__main__":
    run_harness()
