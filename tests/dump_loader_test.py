"""Test harness for dump loader system."""
import argparse
import time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from urllib import request, parse
import json

from mock_memory_router import MockMemoryRouter


# -------- Helpers ---------

def read_lines(path: Path) -> List[str]:
    """Return non-empty lines from a text file."""
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def download_arxiv(subjects: List[str], limit: int) -> List[Dict]:
    """Download articles from arXiv by subject."""
    results: List[Dict] = []
    per_subject = max(1, limit // len(subjects))
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for subj in subjects:
        start = 0
        retrieved = 0
        while retrieved < per_subject:
            batch = min(50, per_subject - retrieved)
            url = (
                "http://export.arxiv.org/api/query?search_query=cat:" f"{subj}" f"&start={start}&max_results={batch}"
            )
            try:
                with request.urlopen(url, timeout=10) as resp:
                    data = resp.read()
            except Exception:
                break
            from xml.etree import ElementTree as ET

            root = ET.fromstring(data)
            entries = root.findall("atom:entry", ns)
            if not entries:
                break
            for entry in entries:
                title = entry.findtext("atom:title", default="", namespaces=ns).strip()
                summary = entry.findtext("atom:summary", default="", namespaces=ns).strip()
                results.append(
                    {
                        "title": title,
                        "summary": summary,
                        "source": "arxiv",
                        "category": subj,
                    }
                )
                retrieved += 1
                if retrieved >= per_subject:
                    break
            start += batch
    return results


def download_wikipedia(categories: List[str], limit: int) -> List[Dict]:
    """Download pages from Wikipedia categories."""
    results: List[Dict] = []
    per_category = max(1, limit // len(categories))
    for cat in categories:
        cont = None
        retrieved = 0
        while retrieved < per_category:
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Category:{cat}",
                "cmlimit": min(50, per_category - retrieved),
                "format": "json",
            }
            if cont:
                params["cmcontinue"] = cont
            url = "https://en.wikipedia.org/w/api.php?" + parse.urlencode(params)
            try:
                with request.urlopen(url, timeout=10) as resp:
                    data = json.load(resp)
            except Exception:
                break
            members = data.get("query", {}).get("categorymembers", [])
            if not members:
                break
            for mem in members:
                pageid = mem["pageid"]
                page_params = {
                    "action": "query",
                    "prop": "extracts",
                    "explaintext": 1,
                    "format": "json",
                    "pageids": pageid,
                }
                page_url = "https://en.wikipedia.org/w/api.php?" + parse.urlencode(page_params)
                try:
                    with request.urlopen(page_url, timeout=10) as p_resp:
                        pdata = json.load(p_resp)
                except Exception:
                    continue
                pages = pdata.get("query", {}).get("pages", {})
                extract = pages.get(str(pageid), {}).get("extract", "")
                results.append(
                    {
                        "title": mem.get("title", ""),
                        "summary": extract,
                        "source": "wikipedia",
                        "category": cat,
                    }
                )
                retrieved += 1
                if retrieved >= per_category:
                    break
            cont = data.get("continue", {}).get("cmcontinue")
            if not cont:
                break
    return results


def transform(records: Iterable[Dict]) -> Tuple[List[Dict], int]:
    """Transform raw records into structured facts."""
    facts: List[Dict] = []
    errors = 0
    for rec in records:
        text = rec.get("summary", "")
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        if not sentences:
            errors += 1
            continue
        for s in sentences[:3]:
            facts.append(
                {
                    "subject": rec.get("title", "unknown"),
                    "predicate": "says",
                    "value": s,
                    "source": rec.get("source"),
                    "category": rec.get("category"),
                }
            )
    return facts, errors


def route(records: Iterable[Dict], router: MockMemoryRouter) -> Tuple[int, int]:
    success = 0
    total = 0
    for rec in records:
        total += 1
        if router.route(rec):
            success += 1
    return success, total - success


def main() -> None:
    parser = argparse.ArgumentParser(description="Dump loader system test harness")
    parser.add_argument("--max-files", type=int, default=50, help="Files per source")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    base = Path(__file__).parent
    arxiv_subjects = read_lines(base / "configs" / "arxiv_subjects.txt")
    wiki_categories = read_lines(base / "configs" / "wikipedia_categories.txt")

    log_file = base / "output_log.txt"

    def log(msg: str) -> None:
        print(msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    t0 = time.time()
    arxiv_records = download_arxiv(arxiv_subjects, args.max_files)
    wiki_records = download_wikipedia(wiki_categories, args.max_files)
    log(f"Downloads - arXiv: {len(arxiv_records)} | Wikipedia: {len(wiki_records)}")

    arxiv_facts, arxiv_err = transform(arxiv_records)
    wiki_facts, wiki_err = transform(wiki_records)
    facts = arxiv_facts + wiki_facts
    transform_errors = arxiv_err + wiki_err
    log(f"Transformations - success: {len(facts)} | errors: {transform_errors}")

    router = MockMemoryRouter(verbose=args.verbose)
    routed, _ = route(facts, router)
    log(f"Routed records: {routed}")
    log(f"Total facts processed: {router.summary()}")

    elapsed = time.time() - t0
    log(f"Elapsed time: {elapsed:.2f}s")


if __name__ == "__main__":
    main()