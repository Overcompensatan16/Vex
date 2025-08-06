"""Batch downloader entry script."""

import argparse
import json
import os
from typing import Dict, List

from audit.audit_logger_factory import AuditLoggerFactory

from cerebral_cortex.source_handlers.external_loaders.preprocessor import process_batch
from cerebral_cortex.source_handlers.download_utils import DEFAULT_DUMP_BASE, download_files
from cerebral_cortex.source_handlers.external_loaders.batch_scheduler import (
    BATCH_SIZE,
    BATCHES_PER_CYCLE,
    add_cli_args,
    batch_scheduler,
)

DL_LOGGERS = {
    "arxiv": AuditLoggerFactory(
        "arxiv_dl", log_path=os.path.join("error_logs", "arxiv_dl.log")
    ),
    "wiki": AuditLoggerFactory(
        "wikipedia_dl", log_path=os.path.join("error_logs", "wikipedia_dl.log")
    ),
}

WIKI_TOPICS = [
    "History_of_philosophy",
    "Physics",
    "Chemistry",
    "Science",
    "Geography",
    "History",
    "Technology",
    "Culture",
    "Emotion",
    "Biography",
    "Mathematics",
    "Linguistics",
]

ARXIV_SUBJECTS = [
    "physics.gen-ph",
    "physics.chem-ph",
    "math.GM",
    "cs.CL",
    "cs.AI",
    "physics.hist-ph",
    "physics.soc-ph",
    "q-bio.NC",
    "physics.bio-ph",
    "stat.ML",
]

MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "download_manifest.json")


def load_manifest(path: str = MANIFEST_PATH) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [{"id": k, **v} for k, v in data.items()]


def main(
    manifest_path: str = MANIFEST_PATH,
    batch_size: int = BATCH_SIZE,
    pause_frequency: int = BATCHES_PER_CYCLE,
    auto: bool = False,
    resume: bool = False,
) -> None:
    manifest = load_manifest(manifest_path)
    enabled = [m for m in manifest if m.get("enabled", True)]
    wiki_records = [
        {
            "id": f"wiki_{topic}",
            "name": f"Wikipedia {topic}",
            "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            "enabled": True,
            "source": "wiki",
        }
        for topic in WIKI_TOPICS
    ]
    arxiv_records = [
        {
            "id": f"arxiv_{subject}",
            "name": f"arXiv {subject}",
            "url": (
                f"http://export.arxiv.org/api/query?search_query=cat:{subject}&max_results=5"
            ),
            "enabled": True,
            "source": "arxiv",
            "subject": subject,
        }
        for subject in ARXIV_SUBJECTS
    ]
    enabled.extend(wiki_records)
    enabled.extend(arxiv_records)

    # Batches download logic with logging
    batches = batch_scheduler(
        enabled,
        dump_base=DEFAULT_DUMP_BASE,
        manifest_path=manifest_path,
        pause=not auto,
        batch_size=batch_size,
        pause_frequency=pause_frequency,
        resume=resume,
        return_batches=True,
    )

    for start, end, batch in batches:
        msg = f"[DumpLoader] Batch {start}-{end} starting download..."
        for logger in DL_LOGGERS.values():
            logger.log_event("downloader", {"message": msg})
        print(msg)

        downloaded = download_files(
            batch, dump_base=DEFAULT_DUMP_BASE, manifest_path=manifest_path
        )

        msg = f"[DumpLoader] Batch {start}-{end} downloaded {len(downloaded)} files"
        for logger in DL_LOGGERS.values():
            logger.log_event("downloader", {"message": msg})
        print(msg)

        msg = f"[DumpLoader] Batch {start}-{end} processing..."
        for logger in DL_LOGGERS.values():
            logger.log_event("downloader", {"message": msg})
        print(msg)

        parsed = process_batch(downloaded, dump_base=DEFAULT_DUMP_BASE)
        msg = f"[DumpLoader] Batch {start}-{end} parser results: {parsed}"
        for logger in DL_LOGGERS.values():
            logger.log_event("downloader", {"message": msg})
        print(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch downloader entry script.")
    parser.add_argument(
        "--manifest-path",
        default=MANIFEST_PATH,
        help="Path to the download manifest JSON file.",
    )
    add_cli_args(parser)
    args = parser.parse_args()
    main(
        manifest_path=args.manifest_path,
        batch_size=args.batch_size,
        pause_frequency=args.pause_frequency,
        auto=args.auto,
        resume=args.resume,
    )
