"""Simple extractor for CIA World Factbook-style data."""

from typing import List
import json

from cerebral_cortex.source_handlers.download_utils import save_dump, log_metadata


SAMPLE_DATA = {
    "France": {
        "population": "67 million",
        "capital": "Paris",
    },
    "Germany": {
        "population": "83 million",
        "capital": "Berlin",
    },
}


def scrape_factbook(domain: str = "geography") -> List[str]:
    """Return declarative statements for a few sample countries."""
    raw = json.dumps(SAMPLE_DATA, ensure_ascii=False).encode("utf-8")
    dump_path = save_dump(raw, "factbook", "sample")
    log_metadata("factbook", dump_path, domain)

    statements: List[str] = []
    for country, fields in SAMPLE_DATA.items():
        pop = fields.get("population")
        if pop:
            statements.append(f"{country} has a population of {pop}.")
        capital = fields.get("capital")
        if capital:
            statements.append(f"The capital of {country} is {capital}.")
    return statements


def parse_dump(path: str) -> List[str]:
    """Parse a downloaded Factbook JSON dump."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []

    statements: List[str] = []
    for country, fields in data.items():
        pop = fields.get("population")
        if pop:
            statements.append(f"{country} has a population of {pop}.")
        capital = fields.get("capital")
        if capital:
            statements.append(f"The capital of {country} is {capital}.")
    return statements
