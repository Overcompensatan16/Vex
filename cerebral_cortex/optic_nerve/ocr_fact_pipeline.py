import json
from cerebral_cortex.temporal_lobe.language_reasoner import reason_over_screen
from cerebral_cortex.fact_generator import records_from_screen_reasoning
from hippocampus.hippocampus_module import HippocampusModule
from memory.memory_store_factory import MemoryStoreFactory


def process_screen_to_memory():
    memory_factory = MemoryStoreFactory()
    hippocampus = HippocampusModule(memory_factory=memory_factory)
    reasoning_result = reason_over_screen()
    records = records_from_screen_reasoning(reasoning_result)
    for rec in records:
        hippocampus.store_record(rec, category="linguistic")
    return records


if __name__ == "__main__":
    recs = process_screen_to_memory()
    print(json.dumps(recs, indent=2))