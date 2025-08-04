from __future__ import annotations

import os
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from typing import Dict, List

from audit.audit_logger_factory import AuditLoggerFactory
from cerebral_cortex.source_handlers.download_utils import (
    DEFAULT_DUMP_BASE,
    log_metadata,
    save_dump,
    read_tracker,
)

LOGGER = AuditLoggerFactory(
    "arxiv_dl", log_path=os.path.join("error_logs", "arxiv_dl.log")
)

ARXIV_API = "http://export.arxiv.org/api/query"

SUBJECT_AREAS: Dict[str, Dict[str, str]] = {
    "physics": {
        "astrophysics": "astro-ph",
        "atomic": "physics.atom-ph",
        "condensed_matter": "cond-mat",
        "general": "physics.gen-ph",
        "optics": "physics.optics",
        "quantum": "quant-ph",
    },
    "math": {
        "algebra": "math.RA",
        "analysis": "math.CA",
        "combinatorics": "math.CO",
        "geometry": "math.DG",
        "number_theory": "math.NT",
    },
    "cs": {
        "ai": "cs.AI",
        "cv": "cs.CV",
        "ml": "cs.LG",
        "hci": "cs.HC",
        "cr": "cs.CR",
        "pl": "cs.PL",
    },
    "misc": {
        "quant_bio": "q-bio",
        "quant_finance": "q-fin",
        "statistics": "stat",
        "eess": "eess",
        "economics": "econ",
    },
}

SUBJECT_CODES: Dict[str, str] = {}
for area, mapping in SUBJECT_AREAS.items():
    for sub, code in mapping.items():
        internal_type = f"{area}.{sub}" if area != "misc" else sub
        SUBJECT_CODES[internal_type] = code

CODE_TO_TYPE: Dict[str, str] = {}
for type_name, code in SUBJECT_CODES.items():
    CODE_TO_TYPE[code] = type_name
    CODE_TO_TYPE[code.split(".")[0]] = type_name


def fetch_subject(
    subject: str,
    *,
    type_key: str | None = None,
    max_results: int = 5,
    domain: str = "science",
    dump_base: str = DEFAULT_DUMP_BASE,
    start: int = 0,
    tracker: Dict[str, int] | None = None,
) -> List[Dict]:
    current = start
    records: List[Dict] = []

    while True:
        query = urllib.parse.urlencode(
            {
                "search_query": f"cat:{subject}",
                "start": str(current),
                "max_results": str(max_results),
            }
        )
        url = f"{ARXIV_API}?{query}"

        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = resp.read()
        except urllib.error.URLError as e:
            LOGGER.log_error("download", f"Failed to download {url}: {e}")
            return []

        dump_path = save_dump(data, "arxiv", subject, dump_base)
        log_metadata("arxiv", dump_path, domain, dump_base)

        try:
            root = ET.fromstring(data)
            ns = {
                "atom": "http://www.w3.org/2005/Atom",
                "arxiv": "http://arxiv.org/schemas/atom",
            }

            entries = root.findall("atom:entry", ns)
            print(f"[ArXiv] Found {len(entries)} entries for {subject}")
            if not entries:
                print(f"[ArXiv] No entries found for subject: {subject}. Skipping...")
                return []

            batch: List[Dict] = []
            for entry in entries:
                title = entry.findtext("atom:title", default="", namespaces=ns).strip()
                summary = entry.findtext("atom:summary", default="", namespaces=ns).strip()
                updated = entry.findtext("atom:updated", default="", namespaces=ns).strip()
                primary = entry.find("arxiv:primary_category", ns)
                category = (
                    primary.attrib.get("term") if primary is not None else "general"
                ).lower()

                if title and summary:
                    batch.append(
                        {
                            "source": "arxiv",
                            "timestamp": updated or datetime.now(timezone.utc).isoformat(),
                            "type": type_key or CODE_TO_TYPE.get(category, category),
                            "subject": title,
                            "predicate": "abstract",
                            "value": summary,
                            "confidence": 0.9,
                        }
                    )

        except ET.ParseError:
            break

        if not batch:
            break

        records.extend(batch)
        current += len(batch)
        if tracker is not None:
            tracker[subject] = current

        if len(batch) < max_results:
            from_date = (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()
            oai_xml = fetch_oai_dump(subject, from_date)
            if oai_xml:
                oai_dump = save_dump(oai_xml, "arxiv_oai", subject, dump_base)
                log_metadata("arxiv_oai", oai_dump, domain, dump_base)
                try:
                    oai_root = ET.fromstring(oai_xml)
                except ET.ParseError:
                    oai_root = None
                if oai_root is not None:
                    oai_ns = {
                        "oai": "http://www.openarchives.org/OAI/2.0/",
                        "arxiv": "http://arxiv.org/OAI/arXiv/",
                    }
                    for rec in oai_root.findall("oai:ListRecords/oai:record", oai_ns):
                        meta = rec.find("oai:metadata/arxiv:arXiv", oai_ns)
                        if meta is None:
                            continue
                        title = meta.findtext("arxiv:title", default="", namespaces=oai_ns).strip()
                        abstract = meta.findtext("arxiv:abstract", default="", namespaces=oai_ns).strip()
                        categories = meta.findtext("arxiv:categories", default="", namespaces=oai_ns)
                        created = meta.findtext("arxiv:created", default="", namespaces=oai_ns).strip()
                        category = categories.split()[0].lower() if categories else "general"
                        if title and abstract:
                            records.append(
                                {
                                    "source": "arxiv",
                                    "timestamp": created + "T00:00:00Z" if created else datetime.now(timezone.utc).isoformat(),
                                    "type": type_key or CODE_TO_TYPE.get(category, category),
                                    "subject": title,
                                    "predicate": "abstract",
                                    "value": abstract,
                                    "confidence": 0.9,
                                }
                            )
            break

    return records


def fetch_all_subjects(
    max_results: int = 5,
    domain: str = "science",
    dump_base: str = DEFAULT_DUMP_BASE,
) -> List[Dict]:
    tracker = read_tracker()
    all_records: List[Dict] = []
    for tk, cat_code in SUBJECT_CODES.items():
        start = tracker.get(cat_code, 0)
        all_records.extend(
            fetch_subject(
                cat_code,
                type_key=tk,
                max_results=max_results,
                domain=domain,
                dump_base=dump_base,
                start=start,
                tracker=tracker,
            )
        )
    return all_records


def parse_dump(path: str, dump_base: str = DEFAULT_DUMP_BASE) -> List[Dict]:
    if not os.path.isabs(path):
        path = os.path.join(dump_base, path)

    try:
        with open(path, "rb") as f:
            data = f.read()
    except Exception:
        return []

    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return []

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    records: List[Dict] = []
    for entry in root.findall("atom:entry", ns):
        title = entry.findtext("atom:title", default="", namespaces=ns).strip()
        summary = entry.findtext("atom:summary", default="", namespaces=ns).strip()
        updated = entry.findtext("atom:updated", default="", namespaces=ns).strip()
        primary = entry.find("arxiv:primary_category", ns)
        category = (primary.attrib.get("term") if primary is not None else "general").lower()
        type_key = CODE_TO_TYPE.get(category) or CODE_TO_TYPE.get(category.split(".")[0], "general")

        if title and summary:
            records.append(
                {
                    "source": "arxiv",
                    "timestamp": updated or datetime.now(timezone.utc).isoformat(),
                    "type": type_key,
                    "subject": title,
                    "predicate": "abstract",
                    "value": summary,
                    "confidence": 0.9,
                }
            )
    return records


def main() -> None:  # pragma: no cover
    records = fetch_all_subjects(max_results=1)
    for rec in records:
        LOGGER.log_event("record", {"type": rec["type"], "subject": rec["subject"]})


if __name__ == "__main__":
    main()
