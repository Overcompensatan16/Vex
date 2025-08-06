from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List

from audit.audit_logger_factory import AuditLoggerFactory
from cerebral_cortex.source_handlers.download_utils import log_metadata, save_dump

LOGGER = AuditLoggerFactory(
    "wikipedia_dl", log_path=os.path.join("error_logs", "wikipedia_dl.log")
)

__all__ = [
    "download_page",
    "download_and_clean",
    "parse_dump",
    "tag_facts",
]


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


def parse_dump(path: str, dump_base: str | None = None) -> List[str]:
    """Load a saved Wikipedia dump and split it into text blocks.

    Parameters
    ----------
    path:
        Path to the dump file. If ``dump_base`` is provided and ``path`` is
        relative, the two are joined.
    dump_base:
        Optional base directory containing dumps. When ``None`` the ``path``
        is assumed to be absolute.

    Returns
    -------
    List[str]
        Paragraph-like text blocks extracted from the dump.
    """

    if dump_base and not os.path.isabs(path):
        path = os.path.join(dump_base, path)

    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()

    blocks = [p.strip() for p in text.split("\n\n") if p.strip()]
    return blocks


def tag_facts(filename: str, block: str, facts: List[Dict]) -> None:
    """Attach simple tags derived from filename and section headers."""

    base = os.path.splitext(filename)[0]
    parts = base.split("_", 2)
    lang = parts[0] if parts else ""
    title = parts[1].replace("_", " ") if len(parts) > 1 else base.replace("_", " ")

    stripped = block.strip().splitlines()[0] if block.strip() else ""
    match = re.match(r"=+\s*(.*?)\s*=+", stripped)
    section = match.group(1).strip() if match else None

    for fact in facts:
        tags = fact.setdefault("tags", [])
        if lang and lang not in tags:
            tags.append(lang)
        if title and title not in tags:
            tags.append(title)
        if section and section not in tags:
            tags.append(section)
