from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import List

from audit.audit_logger_factory import AuditLoggerFactory
from cerebral_cortex.source_handlers.download_utils import log_metadata, save_dump

LOGGER = AuditLoggerFactory(
    "wikipedia_dl", log_path=os.path.join("error_logs", "wikipedia_dl.log")
)


def download_page(title: str, lang: str = "en") -> str:
    """Return the plain-text extract for a Wikipedia page."""
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": 1,
        "format": "json",
        "titles": title,
    }
    url = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.load(resp)
    except urllib.error.URLError as e:
        LOGGER.log_error("download", f"Failed to download {title}: {e}")
        return ""
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    return page.get("extract", "")


def download_and_clean(
    lang: str,
    titles: List[str] | None = None,
    domain: str = "culture",
) -> List[str]:
    """Download selected pages and store them as raw dumps."""
    if titles is None:
        titles = ["Earth"]
    lang = lang.replace("wiki", "")
    paths: List[str] = []
    for title in titles:
        text = download_page(title, lang=lang)
        if not text:
            continue
        path = save_dump(text.encode("utf-8"), "wiki", f"{lang}_{title}")
        log_metadata("wiki", path, domain)
        paths.append(path)
    return paths
