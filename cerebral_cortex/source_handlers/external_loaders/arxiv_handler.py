"""Fetch abstracts from the arXiv API."""

import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import List

from cerebral_cortex.source_handlers.download_utils import save_dump, log_metadata


ARXIV_API = "http://export.arxiv.org/api/query"


def fetch_subject(subject: str, max_results: int = 5, domain: str = "science") -> List[str]:
    """Return title and abstract blocks for a given subject."""
    query = urllib.parse.urlencode({
        "search_query": f"cat:{subject}",
        "max_results": str(max_results),
    })
    url = f"{ARXIV_API}?{query}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = resp.read()
    except urllib.error.URLError:
        return []

    dump_path = save_dump(data, "arxiv", subject)
    log_metadata("arxiv", dump_path, domain)

    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    results: List[str] = []
    for entry in root.findall("atom:entry", ns):
        title = entry.findtext("atom:title", default="", namespaces=ns).strip()
        summary = entry.findtext("atom:summary", default="", namespaces=ns).strip()
        if title and summary:
            results.append(f"{title}: {summary}")
    return results


def parse_dump(path: str) -> List[str]:
    """Parse an arXiv API XML dump."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except Exception:
        return []
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return []
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    results: List[str] = []
    for entry in root.findall("atom:entry", ns):
        title = entry.findtext("atom:title", default="", namespaces=ns).strip()
        summary = entry.findtext("atom:summary", default="", namespaces=ns).strip()
        if title and summary:
            results.append(f"{title}: {summary}")
    return results
