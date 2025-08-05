import json
import os
from multiprocessing import Pool, cpu_count
from typing import Callable, Dict, List

from cerebral_cortex.source_handlers.download_utils import DEFAULT_DUMP_BASE
from cerebral_cortex.fact_generator import generate_facts
from cerebral_cortex.memory_router import store_facts
from audit.audit_logger_factory import AuditLoggerFactory
from cerebral_cortex.source_handlers.transformer_fact_extractor import (
    transform_text,
)


_LOGGERS = {}
_DUMP_BASE = DEFAULT_DUMP_BASE


def _noop_tag(*_args, **_kwargs) -> None:
    """Default tagging function when no wiki tagger is available."""
    return None


# Attempt to import parser functions from optional handler modules. If they are
# missing, fall back to the simple line parser so that module import succeeds.
try:  # pragma: no cover - import robustness
    from cerebral_cortex.source_handlers.external_loaders import wiki_handler

    parse_wiki = getattr(wiki_handler, "parse_dump", None)
    tag_wiki_facts = getattr(wiki_handler, "tag_facts", _noop_tag)
except Exception:  # pragma: no cover - best effort
    parse_wiki = None
    tag_wiki_facts = _noop_tag

try:  # pragma: no cover - import robustness
    from cerebral_cortex.source_handlers.external_loaders import arxiv_handler

    parse_arxiv = getattr(arxiv_handler, "parse_dump", None)
except Exception:  # pragma: no cover - best effort
    parse_arxiv = None


def _init_worker(dump_base: str) -> None:
    global _DUMP_BASE
    _DUMP_BASE = dump_base


def process_record(record: Dict) -> Dict:
    source = record.get("source")
    _path = record.get("path")
    parser: Callable = None

    if source == "wiki":
        parser = parse_wiki
    elif source == "arxiv":
        parser = parse_arxiv

    if not parser:
        return {"path": _path, "count": 0, "error": f"No parser for source: {source}"}

    logger = _LOGGERS.get(source)

    try:
        blocks = parser(_path, dump_base=_DUMP_BASE)
    except Exception as e:
        if logger:
            logger.log_error("parse", f"Error parsing {_path}: {e}")
        return {"path": _path, "count": 0, "error": str(e)}

    total = 0
    aggregated: Dict[str, Dict[str, int]] = {}
    subject = record.get("subject")
    subject_prefix = subject.split(".")[0] if subject else None
    tag_map = {"physics": "physics", "math": "math", "cs": "technology"}
    tag = tag_map.get(subject_prefix) if subject_prefix else None

    for block in blocks:
        try:
            source_type = None
            if isinstance(block, dict):
                if any(k in block for k in ("predicate", "timestamp", "source", "confidence")):
                    facts = [block]
                    block_text = block.get("value", "")
                else:
                    text = block.get("value", "")
                    if not text:
                        continue
                    if logger:
                        logger.log_event("block_length", {"length": len(text)})
                    source_type = block.get("type") or block.get("subject")
                    transformed = transform_text(text)
                    try:
                        facts = generate_facts(
                            transformed, source=source, source_type=source_type
                        )
                        if logger:
                            logger.log_event("facts_generated", {"count": len(facts)})
                    except Exception as e:
                        if logger:
                            logger.log_error(
                                "generate", f"Error generating facts for {_path}: {e}"
                            )
                        continue
                    block_text = text
                    for f in facts:
                        if "subject" in block:
                            f.setdefault("subject", block["subject"])
                        if "predicate" in block:
                            f.setdefault("predicate", block["predicate"])
            else:
                if logger:
                    logger.log_event("block_length", {"length": len(block)})
                if source == "arxiv":
                    source_type = subject
                elif source in {"wiki", "wikipedia"}:
                    source_type = record.get("category") or record.get("domain")
                transformed = transform_text(block)
                try:
                    facts = generate_facts(
                        transformed, source=source, source_type=source_type
                    )
                    if logger:
                        logger.log_event("facts_generated", {"count": len(facts)})
                except Exception as e:
                    if logger:
                        logger.log_error(
                            "generate", f"Error generating facts for {_path}: {e}"
                        )
                    continue
                block_text = block

            if subject:
                for f in facts:
                    f.setdefault("subject", subject)
                    f.setdefault("tags", [])
                    if tag and tag not in f["tags"]:
                        f["tags"].append(tag)
            if source in {"wiki", "wikipedia"}:
                tag_wiki_facts(os.path.basename(_path), block_text, facts)

            stats = store_facts(facts)
            if logger:
                for p, c in stats.items():
                    logger.log_event(
                        "store_facts",
                        {
                            "path": p,
                            "stored": c.get("stored", 0),
                            "duplicate": c.get("skipped", 0),
                        },
                    )
            for p, c in stats.items():
                entry = aggregated.setdefault(p, {"stored": 0, "skipped": 0})
                entry["stored"] += c.get("stored", 0)
                entry["skipped"] += c.get("skipped", 0)
            total += sum(c.get("stored", 0) + c.get("skipped", 0) for c in stats.values())
        except Exception as e:
            logger = _LOGGERS.get(source)
            if logger:
                logger.log_error("routing", f"Fact routing failed for {_path}: {e}")

    if logger:
        logger.log_event(
            "record",
            {"message": f"Stored {total} facts", "file": os.path.basename(_path)},
        )
    return {"path": _path, "count": total, "stats": aggregated}


def _log_results(results: List[Dict]) -> None:
    with open(AUDIT_LOG, "a", encoding="utf-8") as fh:
        for res in results:
            fh.write(json.dumps(res) + "\n")


def process_batch(records: List[Dict], dump_base: str = DEFAULT_DUMP_BASE) -> Dict[str, int]:
    """Parse downloaded dumps and route generated facts in parallel."""
    max_procs = min(max(cpu_count() - 1, 1), 8)
    with Pool(processes=max_procs, initializer=_init_worker, initargs=(dump_base,)) as pool:
        results = pool.map(process_record, records)

    _log_results(results)

    total = sum(r.get("count", 0) for r in results)
    files = sum(1 for r in results if r.get("count", 0) > 0)
    return {"files": files, "total": total}
