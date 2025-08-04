import os
import json
import shutil
from hippocampus.memory.memory_store_factory import MemoryStoreFactory


def test_memory_writer_creates_file_and_appends():
    test_dir = "hippocampus/memory_test"
    factory = MemoryStoreFactory(base_dir=test_dir)
    writer = factory.get_memory_writer("test_module", "test_category")

    record = {"fact": "Water is wet", "type": "observation"}
    writer.append(record)

    path = os.path.join(test_dir, "test_category", "test_module.jsonl")
    assert os.path.exists(path), f"Expected file at {path}, but none found."
    print(f"✅ File created: {path}")

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 1, "Expected exactly 1 line written."
        entry = json.loads(lines[0])
        assert entry["fact"] == "Water is wet"
        assert "_stored" in entry
        print(f"✅ Record stored: {entry}")

    shutil.rmtree(test_dir)


def test_writer_rotation():
    test_dir = "hippocampus/memory_test_rotate"
    factory = MemoryStoreFactory(base_dir=test_dir)
    writer = factory.get_memory_writer("rotate_module", "rotate_category")
    writer.max_size_bytes = 500  # Force rotate quickly

    path = os.path.join(test_dir, "rotate_category", "rotate_module.jsonl")

    for _ in range(20):
        writer.append({"fact": "Filler data"})

    files = os.listdir(os.path.dirname(path))
    jsonl_files = [f for f in files if f.startswith("rotate_module") and f.endswith(".jsonl")]
    print(f"✅ JSONL files found: {jsonl_files}")
    assert len(jsonl_files) >= 2, "Expected rotated files due to size limit."

    shutil.rmtree(test_dir)
