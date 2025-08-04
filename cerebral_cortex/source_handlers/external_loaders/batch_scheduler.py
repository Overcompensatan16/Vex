"""Batch scheduler orchestrating parallel download and processing cycles."""

from __future__ import annotations

import argparse
import json
import os
from multiprocessing import get_context
from typing import Dict, List

from audit.audit_logger_factory import AuditLoggerFactory
from cerebral_cortex.source_handlers.download_utils import download_files, DEFAULT_DUMP_BASE
from cerebral_cortex.source_handlers.external_loaders.preprocessor import process_batch

SCHED_LOGGERS = {
    "arxiv": AuditLoggerFactory(
        "arxiv_dl", log_path=os.path.join("error_logs", "arxiv_dl.log")
    ),
    "wiki": AuditLoggerFactory(
        "wikipedia_dl", log_path=os.path.join("error_logs", "wikipedia_dl.log")
    ),
}

# Paths for memory snapshots and cycle audit summaries
MEMORY_BASE = os.path.normpath(
    os.getenv("MEMORY_BASE", os.path.join(os.path.dirname(__file__), "AI_Memory_Stores"))
)
AI_AUDIT_DIR = os.path.join(os.path.dirname(__file__), "AI_Audit")
os.makedirs(AI_AUDIT_DIR, exist_ok=True)


BATCH_SIZE = 150
WORKER_COUNT = 4
BATCHES_PER_CYCLE = 10

AUDIT_LOG = os.path.join(os.path.dirname(__file__), "download_audit.jsonl")
STATE_PATH = os.path.join(os.path.dirname(__file__), "scheduler_state.json")


def _partition(records: List[Dict], size: int) -> List[List[Dict]]:
    """Split records into fixed-size batches."""
    return [records[i: i + size] for i in range(0, len(records), size)]


def _load_completed(log_path: str = AUDIT_LOG) -> set[int]:
    """Return batch ids that have already been successfully processed."""
    if not os.path.exists(log_path):
        return set()
    completed: set[int] = set()
    with open(log_path, "r", encoding="utf-8") as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("status") != "ok":
                continue
            bid = entry.get("batch")
            if isinstance(bid, int):
                completed.add(bid)
    return completed


def _log_batch(batch_id: int, result: Dict) -> None:
    entry = {"batch": batch_id, **result}
    with open(AUDIT_LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def _run_batch(batch_id: int, records: List[Dict], dump_base: str, manifest_path: str | None) -> Dict:
    try:
        downloaded = download_files(records, dump_base=dump_base, manifest_path=manifest_path)
        result = process_batch(downloaded, dump_base=dump_base)
        entry = {"status": "ok", **result}
    except Exception as exc:  # pragma: no cover - defensive
        entry = {"status": "error", "error": str(exc)}
    _log_batch(batch_id, entry)
    return entry


def _memory_snapshot() -> Dict[str, int]:
    """Return line counts for each memory store JSONL file."""
    snapshot: Dict[str, int] = {}
    if not os.path.exists(MEMORY_BASE):
        return snapshot
    for root, _, files in os.walk(MEMORY_BASE):
        for name in files:
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(root, name)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    count = sum(1 for _ in fh)
            except OSError:
                count = 0
            rel_path = os.path.relpath(path, MEMORY_BASE)
            snapshot[rel_path] = count
    return snapshot


_LAST_SNAPSHOT = _memory_snapshot()


def _load_state(path: str = STATE_PATH) -> Dict:
    """Load scheduler state from disk."""
    if not os.path.exists(path):
        return {"completed_batches": [], "memory_snapshot": _LAST_SNAPSHOT}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            state = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {"completed_batches": [], "memory_snapshot": _LAST_SNAPSHOT}
    if not isinstance(state.get("completed_batches"), list):
        state["completed_batches"] = []
    if not isinstance(state.get("memory_snapshot"), dict):
        state["memory_snapshot"] = _LAST_SNAPSHOT
    return state


def _save_state(completed: set[int], snapshot: Dict[str, int], path: str = STATE_PATH) -> None:
    """Persist scheduler state to disk."""
    state = {
        "completed_batches": sorted(completed),
        "memory_snapshot": snapshot,
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)


def pre_pause_hook(stats: List[Dict]) -> Dict:
    """Compute memory diffs and duplicate counts for the completed cycle."""
    global _LAST_SNAPSHOT
    current = _memory_snapshot()
    diff = {
        path: current.get(path, 0) - _LAST_SNAPSHOT.get(path, 0)
        for path in current
    }
    duplicates = 0
    for res in stats:
        for counts in res.get("path_stats", {}).values():
            duplicates += counts.get("skipped", 0)
    _LAST_SNAPSHOT = current
    return {"memory_diff": diff, "duplicates": duplicates}


def batch_scheduler(
    records: List[Dict],
    dump_base: str = DEFAULT_DUMP_BASE,
    manifest_path: str | None = None,
    pause: bool = True,
    *,
    batch_size: int = BATCH_SIZE,
    pause_frequency: int = BATCHES_PER_CYCLE,
    resume: bool = False,
    return_batches: bool = False,
) -> List[tuple[int, int, List[Dict]]]:
    """Process records in parallel batches with periodic pauses."""
    batches = _partition(records, batch_size)
    completed = _load_completed()
    if resume:
        state = _load_state()
        completed.update(state.get("completed_batches", []))
        global _LAST_SNAPSHOT
        _LAST_SNAPSHOT = state.get("memory_snapshot", _LAST_SNAPSHOT)
    pending = [(i, b) for i, b in enumerate(batches) if i not in completed]
    cycle = 0
    while pending:
        current = pending[:pause_frequency]
        pending = pending[pause_frequency:]
        msg = f"Processing batch group {cycle + 1}"
        for logger in SCHED_LOGGERS.values():
            logger.log_event("scheduler", {"message": msg})
        print(f"\n[Scheduler] {msg}")
        ctx = get_context("spawn")
        with ctx.Pool(processes=WORKER_COUNT) as pool:
            stats_list = pool.starmap(
                _run_batch,
                [(bid, batch, dump_base, manifest_path) for bid, batch in current],
            )
        for (bid, batch), res in zip(current, stats_list):
            if res.get("status") == "ok":
                completed.add(bid)
            else:
                pending.append((bid, batch))
        cycle += 1
        remaining = len(pending)
        summary = pre_pause_hook(stats_list)
        summary["cycle"] = cycle
        audit_path = os.path.join(AI_AUDIT_DIR, f"cycle_{cycle}.json")
        with open(audit_path, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)
        _save_state(completed, _LAST_SNAPSHOT)
        msg = f"Cycle {cycle} complete. {remaining} batches remaining."
        for logger in SCHED_LOGGERS.values():
            logger.log_event("scheduler", {"message": msg})
        print(f"\n[Scheduler] {msg}")
        if remaining and pause:
            input("[Scheduler] Press Enter to continue to the next cycle...")
    _save_state(completed, _LAST_SNAPSHOT)

    if return_batches:
        return [(i * batch_size, min((i + 1) * batch_size, len(records)), batch)
                for i, batch in enumerate(batches)]



def add_cli_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Register scheduler-related CLI arguments on ``parser``."""
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help="Number of records to include in each batch.",
    )
    parser.add_argument(
        "--pause-frequency",
        type=int,
        default=BATCHES_PER_CYCLE,
        help="How many batches to process before pausing.",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Process all cycles without prompting between them.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from previous scheduler_state.json and re-queue failed batches only.",
    )
    return parser


def parse_args(args: List[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for batch scheduler."""
    parser = argparse.ArgumentParser(description="Batch scheduler for downloads and processing.")
    add_cli_args(parser)
    return parser.parse_args(args)


