import json
import os
from collections import defaultdict


class AuditInspector:
    """Read-only helper to inspect audit logs."""

    def __init__(self, max_depth: int = 3, max_files: int = 10):
        self.max_depth = max_depth
        self.max_files = max_files

    def _iter_log_files(self, root_dir: str):
        count = 0
        for current_root, dirs, files in os.walk(root_dir):
            depth = current_root[len(root_dir):].count(os.sep)
            if depth > self.max_depth:
                continue
            for f in files:
                if f.endswith('.jsonl'):
                    yield os.path.join(current_root, f)
                    count += 1
                    if count >= self.max_files:
                        return

    def load_entries(self, root_dir: str) -> list:
        entries = []
        for path in self._iter_log_files(root_dir):
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    for line in fh:
                        entries.append(json.loads(line))
            except Exception:
                continue
        return entries

    def summarize_event_types(self, root_dir: str) -> dict:
        summary = defaultdict(int)
        for entry in self.load_entries(root_dir):
            summary[entry.get('type')] += 1
        return dict(summary)
