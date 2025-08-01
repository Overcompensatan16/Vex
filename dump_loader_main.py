"""Batch downloader entry script."""

import json
import os
from typing import List, Dict

from cerebral_cortex.source_handlers.download_utils import download_files, DEFAULT_DUMP_BASE
from cerebral_cortex.source_handlers.external_loaders.preprocessor import process_batch

BATCH_SIZE = 100
MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "download_manifest.json")


def load_manifest(path: str = MANIFEST_PATH) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [{"id": k, **v} for k, v in data.items()]


def chunk_list(items: List[Dict], size: int) -> List[List[Dict]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def main(manifest_path: str = MANIFEST_PATH) -> None:
    manifest = load_manifest(manifest_path)
    enabled = [m for m in manifest if m.get("enabled", True)]
    batches = chunk_list(enabled, BATCH_SIZE)  # ← define it here
    for idx, batch in enumerate(batches):
        start = idx * BATCH_SIZE
        end = start + len(batch) - 1
        print(f"[DumpLoader] Batch {start}-{end} starting download...")
        downloaded = download_files(batch, dump_base=DEFAULT_DUMP_BASE, manifest_path=manifest_path)
        print(f"[DumpLoader] Batch {start}-{end} downloaded {len(downloaded)} files")
        print(f"[DumpLoader] Batch {start}-{end} processing...")
        parsed = process_batch(downloaded)
        print(f"[DumpLoader] Batch {start}-{end} parser results: {parsed}")


if __name__ == "__main__":
    main()
