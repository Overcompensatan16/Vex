"""Utilities for downloading and cleaning Wikipedia articles."""

import json
import re
import urllib.error
import urllib.request
from typing import List

from cerebral_cortex.source_handlers.download_utils import save_dump, log_metadata


def download_page(title: str, lang: str = "en") -> str:
    """Fetch a single Wikipedia page summary via the REST API."""
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("extract", "")
    except urllib.error.URLError:
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


def parse_dump(path: str) -> List[str]:
    """Parse a downloaded Wikipedia dump file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception:
        return []
    return clean_text(text)
