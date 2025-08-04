# memory/memory_store_factory.py

import os
import json
from datetime import datetime, timezone
from typing import Optional


DEFAULT_BASE = r"E:\AI_Memory_Stores"  # legal NTFS path


class MemoryWriter:
    """Write structured memory facts to modular .jsonl files."""

    def __init__(self, module_name: str, category: str, base_dir: str = DEFAULT_BASE):
        self.module_name = module_name
        self.category = category
        if ":" in base_dir[2:]:
            raise ValueError("Illegal path")
        base_dir = base_dir.replace("\\", os.sep)
        self.base_dir = os.path.normpath(base_dir)
        self.path = os.path.join(base_dir, category, f"{module_name}.jsonl")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.max_size_bytes = 10 * 1024 * 1024  # 10MB default
        self._rotation_index = 0

    def _rotate_if_needed(self) -> None:
        if os.path.exists(self.path) and os.path.getsize(self.path) >= self.max_size_bytes:
            base, ext = os.path.splitext(self.path)
            self._rotation_index += 1
            rotated = f"{base}_{self._rotation_index}{ext}"
            os.rename(self.path, rotated)

    def append(self, record: dict):
        record["_stored"] = datetime.now(timezone.utc).isoformat()
        self._rotate_if_needed()
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


class MemoryStoreFactory:
    """Creates append-only .jsonl memory writers based on category/module."""

    def __init__(self, base_dir: str = "E:/AI_Memory_Stores"):
        self.base_dir = base_dir

    def get_memory_writer(self, module_name: str, category: Optional[str] = "linguistic") -> MemoryWriter:
        return MemoryWriter(module_name, category, self.base_dir)
