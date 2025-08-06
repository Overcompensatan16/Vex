from __future__ import annotations

import os
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, Iterable, List

from audit.audit_logger_factory import AuditLoggerFactory
from cerebral_cortex.source_handlers.download_utils import (
    DEFAULT_DUMP_BASE,
    log_metadata,
    save_dump,
)

LOGGER = AuditLoggerFactory(
    "arxiv_dl", log_path=os.path.join("error_logs", "arxiv_dl.log")
)

ARXIV_API = "http://export.arxiv.org/api/query"

# Legacy mapping kept for compatibility; currently unused.
CODE_TO_TYPE: Dict[str, str] = {}


__all__ = ["fetch_subject", "parse_dump", "fetch_all_subjects"]


def fetch_subject(
    subject: str,
    *,
    max_results: int = 5,
    domain: str = "science",
    dump_base: str = DEFAULT_DUMP_BASE,
) -> str | None:
    """Download raw metadata for an arXiv subject.

    The previous implementation attempted to parse and classify the returned
    records.  That functionality has been removed so this function now simply
    downloads the feed and stores it on disk.
    """

    query = urllib.parse.urlencode(
        {
            "search_query": f"cat:{subject}",
            "start": "0",
            "max_results": str(max_results),
        }
    )
    url = f"{ARXIV_API}?{query}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = resp.read()
    except urllib.error.URLError as e:
        LOGGER.log_error("download", f"Failed to download {url}: {e}")
        return None

    dump_path = save_dump(data, "arxiv", subject, dump_base)
    log_metadata("arxiv", dump_path, domain, dump_base)
    return dump_path


def parse_dump(path: str, dump_base: str | None = None) -> List[Dict]:
    """Parse a stored arXiv Atom feed into structured blocks.

    Parameters
    ----------
    path:
        Path to the saved dump file.  If ``dump_base`` is provided and ``path``
        is not absolute, the two are joined.
    dump_base:
        Optional base directory used when ``path`` is relative.

    Returns
    -------
    List[Dict]
        Each dictionary contains at least a ``value`` key holding the
        concatenated title and summary of an entry.  A ``subject`` key is added
        when category information is available.
    """

    full_path = path
    if dump_base and not os.path.isabs(path):
        full_path = os.path.join(dump_base, path)

    with open(full_path, "rb") as fh:
        data = fh.read()

    root = ET.fromstring(data)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    blocks: List[Dict] = []

    for entry in root.findall("atom:entry", ns):
        title_el = entry.find("atom:title", ns)
        summary_el = entry.find("atom:summary", ns)
        title = (title_el.text or "").strip() if title_el is not None else ""
        summary = (summary_el.text or "").strip() if summary_el is not None else ""
        text = f"{title}\n\n{summary}".strip()

        block: Dict[str, str] = {"value": text}

        category_el = entry.find("atom:category", ns)
        if category_el is not None:
            subject = category_el.attrib.get("term")
            if subject:
                block["subject"] = subject

        blocks.append(block)

    return blocks


def fetch_all_subjects(
    subjects: Iterable[str],
    *,
    max_results: int = 5,
    dump_base: str = DEFAULT_DUMP_BASE,
) -> List[Dict]:
    """Fetch and parse multiple arXiv subjects.

    This convenience helper downloads each subject's feed via
    :func:`fetch_subject`, parses the resulting XML with :func:`parse_dump`, and
    aggregates the structured blocks.  Blocks are annotated with the originating
    subject when available.

    Parameters
    ----------
    subjects:
        Iterable of arXiv subject codes to download.
    max_results:
        Maximum number of results per subject feed.
    dump_base:
        Directory where dumps are stored.

    Returns
    -------
    List[Dict]
        All parsed blocks for the requested subjects.
    """

    records: List[Dict] = []
    for subj in subjects:
        path = fetch_subject(subj, max_results=max_results, dump_base=dump_base)
        if not path:
            continue
        try:
            blocks = parse_dump(path, dump_base=dump_base)
        except Exception as exc:  # pragma: no cover - best effort logging
            LOGGER.log_error("parse", f"Failed to parse {path}: {exc}")
            continue
        for block in blocks:
            block.setdefault("subject", subj)
            records.append(block)
    return records