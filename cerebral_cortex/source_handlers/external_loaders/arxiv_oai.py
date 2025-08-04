from __future__ import annotations

import os
import urllib.error
import urllib.parse
import urllib.request

from audit.audit_logger_factory import AuditLoggerFactory

OAI_BASE = "https://export.arxiv.org/oai2"

LOGGER = AuditLoggerFactory(
    "arxiv_dl", log_path=os.path.join("error_logs", "arxiv_dl.log")
)


def fetch_oai_dump(category: str, from_date: str) -> bytes:
    """Return raw XML bytes for an arXiv category using OAI-PMH.

    Parameters
    ----------
    category:
        The arXiv category code (e.g. ``cs.AI``).
    from_date:
        Start date for harvesting in ``YYYY-MM-DD`` format.
    """
    params = {
        "verb": "ListRecords",
        "metadataPrefix": "arXiv",
        "set": category,
        "from": from_date,
    }
    url = f"{OAI_BASE}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            return resp.read()
    except urllib.error.URLError as e:
        LOGGER.log_error("download", f"Failed to fetch OAI-PMH dump {url}: {e}")
        return b""
