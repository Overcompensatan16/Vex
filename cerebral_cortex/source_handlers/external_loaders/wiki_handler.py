from __future__ import annotations
import time

"""Utilities for downloading, parsing and cleaning Wikipedia articles.

This module can download the massive ``enwiki`` article dump and parse it in a
streaming multithreaded fashion.  It is intentionally light‑weight, so it can be
used both by the batch loaders and as a standalone script.
"""


import argparse
import bz2
import json
import os
import re
import html
import shutil
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Iterable, Iterator, List, Tuple

if __package__ in (None, ""):
    # Allow running the file directly via ``python wiki_handler.py``
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

try:  # ``mwparserfromhell`` is preferred for stripping wiki markup.
    import mwparserfromhell  # type: ignore
except Exception:  # pragma: no cover - fallback when package missing
    mwparserfromhell = None  # type: ignore

from cerebral_cortex.source_handlers.download_utils import save_dump, log_metadata


# ---------------------------------------------------------------------------
# Download helpers

DEFAULT_DUMP_URL = (
    "https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2"
)
# Location of the raw dump on the external drive.  The path mirrors the layout
# used by the other loaders in this repository.
DEFAULT_RAW_DIR = os.path.normpath(r"E:/dumps/_Raw/Wikipedia")


def download_latest_dump(dest_dir: str = DEFAULT_RAW_DIR, url: str = DEFAULT_DUMP_URL) -> str:
    """Download the latest English Wikipedia article dump.

    Parameters
    ----------
    dest_dir:
        Directory where the file should be stored.  The resulting file is named
        ``raw_<timestamp>.bz2``.
    url:
        Dump URL to fetch.  Exposed for testing or mirrors.

    Returns
    -------
    str
        Path to the downloaded dump file.
    """

    os.makedirs(dest_dir, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest_path = os.path.join(dest_dir, f"raw_{ts}.bz2")

    try:
        with urllib.request.urlopen(url) as resp, open(dest_path, "wb") as fh:
            shutil.copyfileobj(resp, fh)
    except urllib.error.URLError as e:  # pragma: no cover - network errors
        print(f"Failed to download dump: {e}")
        raise

    return os.path.normpath(dest_path)


# ---------------------------------------------------------------------------
# Parsing utilities

def _strip_markup(text: str) -> str:
    """Remove wiki markup from ``text``.

    ``mwparserfromhell`` is used when available.  A very small regex based
    fallback is provided to keep the function working in limited environments.
    """

    if mwparserfromhell:
        return mwparserfromhell.parse(text).strip_code()

    # Fallback: remove templates and HTML tags, then strip brackets.
    text = re.sub(r"\{\{[^}]+}}", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("[", "").replace("]", "")
    return text


def _process_page(xml: bytes) -> Tuple[str, str] | None:
    """Extract a ``(title, clean_text)`` pair from serialized ``page`` XML."""

    try:
        elem = ET.fromstring(xml)
    except ET.ParseError:
        return None

    title = elem.findtext("./{*}title") or ""
    ns = elem.findtext("./{*}ns")
    if ns != "0":  # skip talk/user/meta pages
        return None
    if elem.find("./{*}redirect") is not None:
        return None

    text_el = elem.find(".//{*}text")
    if text_el is None or not text_el.text:
        return None

    raw = text_el.text
    lower_title = title.lower()
    lower_raw = raw.lower()
    if "(disambiguation)" in lower_title or "{{disambiguation" in lower_raw:
        return None
    if "{{disambig" in lower_raw or "{{stub" in lower_raw:
        return None

    clean = _strip_markup(raw)
    clean = re.sub(r"\n{2,}", "\n", clean).strip()
    if not clean:
        return None
    return title, clean


def iter_dump_pages(path: str, workers: int = 8) -> Iterator[Tuple[str, str]]:
    """Yield ``(title, clean_text)`` pairs from ``path``.

    The XML dump is streamed and individual pages are cleaned concurrently using
    a thread pool so memory usage stays modest even for the multi‑gigabyte
    archive.
    """

    opener = bz2.open if path.endswith(".bz2") else open
    with opener(path, "rb") as fh:
        context = ET.iterparse(fh, events=("end",))
        _, root = next(context)  # Prime the parser and grab root for clearing

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for event, elem in context:
                if elem.tag.endswith("page"):
                    page_xml = ET.tostring(elem, encoding="utf-8")
                    futures.append(executor.submit(_process_page, page_xml))
                    elem.clear()
                    root.clear()
                    if len(futures) >= workers * 5:
                        for f in as_completed(futures):
                            res = f.result()
                            if res:
                                yield res
                        futures.clear()

            for f in as_completed(futures):
                res = f.result()
                if res:
                    yield res


def parse_dump(path: str, dump_base: str | None = None) -> List[str]:
    """Return cleaned text blocks from a dump file.

    This retains the previous ``List[str]`` interface for compatibility with the
    batch preprocessor while internally relying on :func:`iter_dump_pages`.
    """

    if dump_base and not os.path.isabs(path):
        path = os.path.join(dump_base, path)

        # Stream full XML dumps via iter_dump_pages.
    if path.endswith((".xml", ".xml.bz2", ".bz2")):
        return [text for _, text in iter_dump_pages(path)]

        # Otherwise treat as a single-page HTML or plain text file.
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except OSError:
        return []

        # Normalize common HTML tags to newlines before stripping markup.
    raw = re.sub(r"<(?:br|p|div|li|h\d)[^>]*>", "\n", raw, flags=re.IGNORECASE)
    raw = re.sub(r"</(?:p|div|li|h\d)>", "\n", raw, flags=re.IGNORECASE)

    text = _strip_markup(raw)
    text = html.unescape(text)
    return clean_text(text)

    # Otherwise treat as a single-page HTML or text file.
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except OSError:
        return []

    raw = re.sub(r"<(?:br|p|div|li|h\d)[^>]*>", "\n", raw, flags=re.IGNORECASE)
    raw = re.sub(r"</(?:p|div|li|h\d)>", "\n", raw, flags=re.IGNORECASE)

    text = _strip_markup(raw)
    text = html.unescape(text)
    return clean_text(text)


def download_page(title: str, lang: str = "en") -> str:
    """Fetch a single Wikipedia page summary via the REST API."""
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("extract", "")
    except urllib.error.URLError as e:
        try:
            from audit.audit_logger_factory import AuditLoggerFactory
            LOGGER = AuditLoggerFactory("wiki_dl", log_path=os.path.join("error_logs", "wiki_dl.log"))
        except Exception:
            LOGGER = None
        if LOGGER:
            LOGGER.log_error("download", f"Failed to download {url}: {e}")
        else:
            print(f"Failed to download {url}: {e}")
        return ""



def clean_text(text: str) -> List[str]:
    """Remove references and split text into paragraphs."""
    text = re.sub(r"\[[^]]+]", "", text)
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    return paragraphs


def download_and_clean(lang: str, titles: List[str] | None = None, domain: str = "culture") -> List[str]:
    """Download pages and return cleaned paragraph blocks."""
    if titles is None:
        titles = ["Earth"]
    cleaned: List[str] = []
    lang = lang.replace("wiki", "")
    for title in titles:
        text = download_page(title, lang=lang)
        if not text:
            continue
        path = save_dump(text.encode("utf-8"), "wiki", f"{lang}_{title}")
        log_metadata("wiki", path, domain)
        cleaned.extend(clean_text(text))
    return cleaned


def classify_article(file: str, content: str) -> str:
    """Return a routing category for a Wikipedia article."""

    fname = os.path.basename(file).lower()
    lower_content = content.lower()

    if any(k in fname or k in lower_content for k in ["history", "politics", "language"]):
        return "wiki.historical"
    if any(
        k in fname or k in lower_content
        for k in ["science", "physics", "chemistry", "biology", "mathematics"]
    ):
        return "wiki.scientific"
    return "wiki.general"


def tag_facts(file: str, content: str, facts: List[dict]) -> None:
    """Annotate facts with topical categories for routing.

    The classifier is invoked on ``file`` and ``content`` to determine the
    appropriate category before facts are routed to memory.
    """

    category = classify_article(file, content)
    for fact in facts:
        fact["type"] = category
        fact["source"] = "wikipedia"


def main(argv: Iterable[str] | None = None) -> None:
    """CLI entry point for parsing a Wikipedia dump.

    Example
    -------
    ``python wiki_handler.py --dump <path/to/enwiki-latest-pages-articles.xml.bz2>``
    """

    parser = argparse.ArgumentParser(description="Wikipedia dump parser")
    parser.add_argument(
        "--dump",
        help="Path to dump file (.bz2). If omitted with --download, only download",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download the latest dump to the default location and exit",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    path: str | None = None
    if args.download:
        path = download_latest_dump()
        print(path)
        if not args.dump:
            return

    dump_path = args.dump or path
    if not dump_path:
        parser.error("--dump path required unless only downloading")
        return

    # Import heavy dependencies lazily so ``--help`` or ``--download`` work
    from cerebral_cortex.fact_generator import generate_facts
    from cerebral_cortex.memory_router import store_facts

    for title, text in iter_dump_pages(dump_path):
        facts = generate_facts(text, source="wiki")
        tag_facts(title, text, facts)
        store_facts(facts)


if __name__ == "__main__":  # pragma: no cover - CLI behavior
    main()
