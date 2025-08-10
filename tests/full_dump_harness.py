"""
Unified pipeline test harness for wiki/arxiv dump processing
============================================================

Features:
- Actually downloads and parses real files (wiki/arxiv URLs)
- Annotated at every step (download, parse, preprocess, transform, store)
- Flags hard/soft failures, logs warnings/errors per stage
- Tracks memory routing using the real FactRouter and store
- Prints detailed batch, per-record, and per-fact statistics
- Retains other test files for backup

Usage:
    python tests/full_pipeline_harness.py --log --dump-base ./test_dumps
    # Optional: --wiki-urls, --arxiv-urls, --max-files, etc.

Notes:
- You MUST provide valid URLs for wiki/arxiv, or use the defaults.
- All steps are wrapped with try/except and print annotations.
"""

import os
import sys
import argparse
import json
import traceback
from datetime import datetime

# === Pipeline Imports ===
from cerebral_cortex.source_handlers.download_utils import download_files, DEFAULT_DUMP_BASE
from cerebral_cortex.source_handlers.external_loaders.arxiv_handler import parse_dump as parse_arxiv
from cerebral_cortex.source_handlers.external_loaders.wiki_handler import parse_dump as parse_wiki, tag_facts as tag_wiki_facts
from cerebral_cortex.source_handlers.external_loaders.preprocessor import transform_text, generate_facts
from cerebral_cortex.fact_generator.fact_generator import generate_facts as generator_generate_facts
from hippocampus.fact_router import FactRouter, FACT_OUTPUT_PATHS

# === Default URLs for tests ===
DEFAULT_WIKI_URLS = [
    "https://en.wikipedia.org/wiki/Number_theory",
    "https://en.wikipedia.org/wiki/Organic_chemistry",
    "https://en.wikipedia.org/wiki/Indian_philosophy",
]
DEFAULT_ARXIV_URLS = [
    "https://arxiv.org/abs/2101.00001",
    "https://arxiv.org/abs/1810.04805",
]

def download_and_annotate(urls, dump_base, kind, log):
    """Download files and annotate each stage."""
    log(f"--- Downloading {kind} files ---")
    try:
        files = download_files(urls, dump_base)
        log(f"{kind} files downloaded: {files}")
        return files
    except Exception as e:
        log(f"[FAIL] {kind} download failed: {e}", error=True)
        traceback.print_exc()
        return []

def parse_and_annotate(paths, kind, log):
    """Parse downloaded files and annotate each stage."""
    log(f"--- Parsing {kind} dumps ---")
    parsed_blocks = []
    for path in paths:
        try:
            if kind == "wiki":
                blocks = parse_wiki(path)
            elif kind == "arxiv":
                blocks = parse_arxiv(path)
            else:
                log(f"[WARN] Unknown kind for parsing: {kind}", error=False)
                continue
            log(f"Parsed {len(blocks)} blocks from {path}")
            parsed_blocks.append((path, blocks))
        except Exception as e:
            log(f"[FAIL] Parse failed for {path}: {e}", error=True)
            traceback.print_exc()
            parsed_blocks.append((path, []))
    return parsed_blocks

def preprocess_and_annotate(path, blocks, kind, log):
    """Run preprocessing, transformation, fact generation, tagging, and annotate."""
    log(f"--- Preprocessing {kind} file: {path} ---")
    all_facts = []
    errors = []
    for i, block in enumerate(blocks):
        try:
            # Transform and generate facts
            transformed = transform_text(block if isinstance(block, str) else block.get("value", ""))
            facts = generator_generate_facts(transformed, source=kind)
            log(f"Transformed block {i} ({len(transformed) if hasattr(transformed, '__len__') else 'n/a'} chars), generated {len(facts)} facts")
            if kind == "wiki":
                tag_wiki_facts(os.path.basename(path), block, facts)
            all_facts.extend(facts)
        except Exception as e:
            log(f"[SOFT FAIL] Block {i} preprocessing failed: {e}", error=False)
            traceback.print_exc()
            errors.append({"block": i, "error": str(e)})
    if not all_facts:
        log(f"[HARD FAIL] No facts produced for {path}", error=True)
    return all_facts, errors

def route_and_store_facts(facts, router, log):
    """Route and store facts via FactRouter, logging each operation."""
    stats = {"stored": 0, "duplicates": 0, "errors": 0, "destinations": {}}
    for i, fact in enumerate(facts):
        try:
            fact.setdefault("timestamp", datetime.now().isoformat())
            stored, path = router.route_fact(fact)
            if stored:
                stats["stored"] += 1
                stats["destinations"].setdefault(path, 0)
                stats["destinations"][path] += 1
                log(f"[OK] Fact {i} routed and stored in {path}")
            else:
                stats["duplicates"] += 1
                log(f"[WARN] Fact {i} duplicate, not stored (route: {path})", error=False)
        except Exception as e:
            stats["errors"] += 1
            log(f"[FAIL] Fact {i} routing error: {e}", error=True)
            traceback.print_exc()
    return stats

def print_stats(stats, log):
    log(f"\n--- Batch Results ---")
    log(json.dumps(stats, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Unified, annotated wiki/arxiv pipeline test harness")
    parser.add_argument("--dump-base", default=DEFAULT_DUMP_BASE, help="Directory for downloaded dumps")
    parser.add_argument("--wiki-urls", nargs="*", default=DEFAULT_WIKI_URLS, help="List of Wikipedia URLs")
    parser.add_argument("--arxiv-urls", nargs="*", default=DEFAULT_ARXIV_URLS, help="List of Arxiv URLs")
    parser.add_argument("--max-files", type=int, default=3, help="Maximum files per source")
    parser.add_argument("--log", action="store_true", help="Print detailed logs")
    args = parser.parse_args()

    dump_base = args.dump_base
    wiki_urls = args.wiki_urls[:args.max_files]
    arxiv_urls = args.arxiv_urls[:args.max_files]

    os.makedirs(dump_base, exist_ok=True)

    def log(msg, error=False):
        prefix = "[ERROR]" if error else "[INFO]"
        print(f"{prefix} {msg}")

    # Use actual FactRouter (memory store) for routing
    router = FactRouter()

    # Download
    wiki_paths = download_and_annotate(wiki_urls, dump_base, "wiki", log)
    arxiv_paths = download_and_annotate(arxiv_urls, dump_base, "arxiv", log)

    # Parse
    parsed_wiki = parse_and_annotate(wiki_paths, "wiki", log)
    parsed_arxiv = parse_and_annotate(arxiv_paths, "arxiv", log)

    # Preprocess, transform, generate facts, tag, route, store
    batch_stats = {"wiki": [], "arxiv": [], "errors": []}

    for path, blocks in parsed_wiki:
        facts, errors = preprocess_and_annotate(path, blocks, "wiki", log)
        route_stats = route_and_store_facts(facts, router, log)
        batch_stats["wiki"].append({
            "file": path,
            "facts": len(facts),
            "errors": errors,
            "route_stats": route_stats
        })

    for path, blocks in parsed_arxiv:
        facts, errors = preprocess_and_annotate(path, blocks, "arxiv", log)
        route_stats = route_and_store_facts(facts, router, log)
        batch_stats["arxiv"].append({
            "file": path,
            "facts": len(facts),
            "errors": errors,
            "route_stats": route_stats
        })

    print_stats(batch_stats, log)
    log("\n[COMPLETE] Full pipeline test finished. Check logs and output files for details.")

if __name__ == "__main__":
    main()
