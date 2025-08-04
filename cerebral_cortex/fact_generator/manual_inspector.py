import os
import argparse
from typing import Dict, List

from audit.audit_logger_factory import AuditLoggerFactory
from hippocampus.fact_router import FactRouter, FACT_OUTPUT_PATHS

from cerebral_cortex.source_handlers.external_loaders.arxiv_handler import (
    parse_dump as parse_arxiv,
)
from cerebral_cortex.source_handlers.external_loaders.wiki_handler import (
    parse_dump as parse_wiki,
    tag_facts as tag_wiki_facts,
)
from cerebral_cortex.source_handlers.download_utils import (
    DEFAULT_DUMP_BASE,
    download_files,
)
from cerebral_cortex.source_handlers.external_loaders.dump_loader_main import (
    WIKI_TOPICS,
    ARXIV_SUBJECTS,
)
from cerebral_cortex.source_handlers.external_loaders.preprocessor import (
    _init_worker,
)
from cerebral_cortex.fact_generator.fact_generator import generate_facts
from cerebral_cortex.memory_router import store_facts


LOGGER = AuditLoggerFactory("manual_inspector")


def _configure_router(dest: str) -> None:
    """Rewrite :class:`FactRouter` paths beneath ``dest``."""

    router = FactRouter()
    for key, path in list(router.routes.items()):
        new_path = os.path.normpath(os.path.join(dest, os.path.basename(path)))
        router.routes[key] = new_path
        FACT_OUTPUT_PATHS[key] = new_path
        os.makedirs(os.path.dirname(new_path), exist_ok=True)


def _process_record(record: Dict) -> Dict:
    """Parse ``record['path']`` and store generated facts.

    Returns a dictionary with processing statistics. Errors are logged via
    :data:`LOGGER` and also returned in the result.
    """

    path = record.get("path")
    source = record.get("source")
    parser = parse_arxiv if source == "arxiv" else parse_wiki
    parser_name = (
        "external_loaders.arxiv_handler.parse_dump"
        if source == "arxiv"
        else "external_loaders.wiki_handler.parse_dump"
    )

    try:
        blocks = parser(path)
    except Exception as exc:  # pragma: no cover - best effort logging
        LOGGER.log_error("parse", f"Failed to parse {path}: {exc}")
        return {"path": path, "count": 0, "error": str(exc)}

    facts: List[dict] = []
    if source == "arxiv":
        for rec in blocks:
            if any(k in rec for k in ("predicate", "timestamp", "source", "confidence")):
                facts.append(rec)
            else:
                text = rec.get("value", "")
                facts.extend(
                    generate_facts(text, source="arxiv", source_type=rec.get("type") or rec.get("subject"))
                )
    else:
        for block in blocks:
            gen = generate_facts(block, source="wiki")
            tag_wiki_facts(os.path.basename(path), block, gen)
            facts.extend(gen)

    if not facts:
        LOGGER.log_error("facts", f"No facts produced for {path}")
        return {"path": path, "count": 0, "error": "no facts"}

    stats = store_facts(facts)
    stored = sum(s["stored"] for s in stats.values())
    dest_paths = ", ".join(stats.keys())
    print(f"Loaded {path}; parser={parser_name}; facts={stored}; dest={dest_paths}")
    return {"path": path, "count": stored, "stats": stats}


def process_records(records: List[Dict], dest: str = r"E:/AI_Memory_Stores/Test") -> None:
    """Process a sequence of record dictionaries."""

    _configure_router(dest)
    _init_worker(DEFAULT_DUMP_BASE)

    for rec in records:
        result = _process_record(rec)
        if result.get("count", 0) == 0 and result.get("error"):
            LOGGER.log_error("process", f"{rec['path']}: {result['error']}")


def auto_run(dest: str = r"E:/AI_Memory_Stores/Test") -> None:
    """Automatically download and process sample Wikipedia and arXiv files."""

    wiki_topics = WIKI_TOPICS[:10]
    arxiv_subjects = ARXIV_SUBJECTS[:10]

    wiki_records = [
        {
            "id": f"wiki_{topic}",
            "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            "source": "wiki",
        }
        for topic in wiki_topics
    ]

    arxiv_records = [
        {
            "id": f"arxiv_{subject}",
            "url": f"http://export.arxiv.org/api/query?search_query=cat:{subject}&max_results=5",
            "source": "arxiv",
            "subject": subject,
        }
        for subject in arxiv_subjects
    ]

    downloaded = download_files(wiki_records + arxiv_records, dump_base=DEFAULT_DUMP_BASE)
    records = [
        {"path": d["path"], "source": d.get("source"), "subject": d.get("subject")}
        for d in downloaded
    ]
    process_records(records, dest=dest)


def main(argv: List[str] | None = None) -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(description="Manual fact inspection utility")
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Process provided dump files instead of automatic download",
    )
    parser.add_argument("files", nargs="*", help="Dump files to inspect")
    parser.add_argument(
        "--dest",
        default=r"E:/AI_Memory_Stores/Test",
        help="Base directory for routed facts",
    )
    args = parser.parse_args(argv)

    if args.manual:
        if not args.files:
            parser.error("files required in manual mode")
        records: List[Dict] = []
        for file in args.files:
            src = "wiki"
            try:
                if parse_arxiv(file):
                    src = "arxiv"
            except Exception:
                pass
            records.append({"path": file, "source": src})
        process_records(records, dest=args.dest)
    else:
        auto_run(dest=args.dest)


if __name__ == "__main__":
    main()
