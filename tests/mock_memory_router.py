"""Mock memory router for test harness."""
import os
import json
from typing import Dict, List

TEST_MEMORY_PATH = os.path.normpath(r"E:/AI_Memory_Stores/Test")
os.makedirs(TEST_MEMORY_PATH, exist_ok=True)

class MockMemoryRouter:
    """File-based router for dumping test records into category-tagged jsonl files."""

    def __init__(self, verbose: bool = False):
        self.records: List[Dict] = []
        self.verbose = verbose

    def route(self, record: Dict) -> bool:
        """Route a fact record into E:/AI_Memory_Stores/Test. Returns True on success."""
        required = {"subject", "predicate", "value"}
        if not required.issubset(record):
            return False

        self.records.append(record)

        # Build filepath by category
        cat = record.get("category", "uncategorized").replace("/", "_")
        filename = f"{cat}.jsonl"
        filepath = os.path.join(TEST_MEMORY_PATH, filename)

        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            if self.verbose:
                print(f"[MockMemoryRouter] Routed to {filename}: {record}")
            return True
        except Exception as e:
            if self.verbose:
                print(f"[MockMemoryRouter] ERROR writing record: {e}")
            return False

    def summary(self) -> int:
        """Return the number of routed records."""
        return len(self.records)
