from __future__ import annotations

import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict

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
