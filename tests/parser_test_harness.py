#!/usr/bin/env python3
"""CLI test harness for subject-specific parsers.

This script routes input sentences to the appropriate subject parser, detects
opinions, and stores results in the configured memory stores. It prints
colour-coded debug information and optionally logs to a JSONL file.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import re
import sys
import time
from datetime import datetime
from typing import Callable, Dict, List, Tuple
from hippocampus.fact_router import FactRouter

BASE_MEMORY_PATH = os.path.normpath(r"E:\AI_Memory_Stores")

FACT_GEN_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "cerebral_cortex", "fact_generator", "fact_generator.py")
)


with open(FACT_GEN_PATH, "r", encoding="utf-8") as fact_file:
    tree = ast.parse(fact_file.read(), FACT_GEN_PATH)

opinion_nodes = [
    n
    for n in tree.body
    if isinstance(n, ast.Assign)
    and any(getattr(t, "id", "") == "OPINION_MARKERS" for t in n.targets)
]
is_opinion_node = next(
    n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "is_opinion"
)
module = ast.Module(body=opinion_nodes + [is_opinion_node], type_ignores=[])
global_ns: Dict[str, object] = {}
exec(compile(module, FACT_GEN_PATH, "exec"), global_ns)
is_opinion = global_ns["is_opinion"]

SUBJECT_PARSER_DIR = os.path.join(
    os.path.dirname(__file__),
    "cerebral_cortex",
    "temporal_lobe",
    "subject_parsers",
)


def _load_parser(module_name: str, func_name: str):
    path = os.path.join(SUBJECT_PARSER_DIR, f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return getattr(mod, func_name)


parse_bio_text = _load_parser("bio_parser", "parse_bio_text")
parse_chemistry_text = _load_parser("chemistry_parser", "parse_chemistry_text")
parse_conservation_text = _load_parser("conservation_parser", "parse_conservation_text")
parse_cs_text = _load_parser("cs_parser", "parse_cs_text")
parse_econ_text = _load_parser("econ_parser", "parse_econ_text")
parse_eess_text = _load_parser("eess_parser", "parse_eess_text")
parse_game_theory_text = _load_parser("game_theory_parser", "parse_game_theory_text")
parse_geo_text = _load_parser("geo_parser", "parse_geo_text")
parse_history_text = _load_parser("history_parser", "parse_history_text")
parse_law_text = _load_parser("law_parser", "parse_law_text")
parse_math_text = _load_parser("math_parser", "parse_math_text")
parse_philosophy_text = _load_parser("philosophy_parser", "parse_philosophy_text")
parse_physics_text = _load_parser("physics_parser", "parse_physics_text")
parse_stats_text = _load_parser("stats_parser", "parse_stats_text")


PARSER_FUNCS: Dict[str, Callable[[str], List[Dict]]] = {
    "physics": parse_physics_text,
    "math": parse_math_text,
    "chemistry": parse_chemistry_text,
    "bio": parse_bio_text,
    "environment": parse_eess_text,
    "conservation": parse_conservation_text,
    "philosophy": parse_philosophy_text,
    "geo": parse_geo_text,
    "history": parse_history_text,
    "law": parse_law_text,
    "econ": parse_econ_text,
    "game_theory": parse_game_theory_text,
    "cs": parse_cs_text,
    "stats": parse_stats_text,
    "eess": parse_eess_text,
}


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"


def color_text(text: str, color: str) -> str:
    return f"{color}{text}{Colors.RESET}"


def split_sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def prepare_router() -> FactRouter:
    router = FactRouter()
    base = getattr(router, "_BASE_DIR", BASE_MEMORY_PATH)
    opinion_path = os.path.normpath(os.path.join(base, "opinions", "opinions.jsonl"))
    os.makedirs(os.path.dirname(opinion_path), exist_ok=True)
    router.routes["opinions"] = opinion_path
    return router


def make_logger(log_to_file: bool):
    file_handle = None
    if log_to_file:
        log_file = os.path.normpath(os.path.join(BASE_MEMORY_PATH, "parser_test_debug.jsonl"))
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handle = open(log_file, "a", encoding="utf-8")

    def _log(level: str, message: str, **extra: Dict):
        ts = datetime.now().isoformat()
        entry = {"timestamp": ts, "level": level, "message": message}
        if extra:
            entry["extra"] = extra
        color = {"INFO": Colors.GREEN, "WARN": Colors.YELLOW, "ERROR": Colors.RED}.get(level, Colors.RESET)
        print(color_text(f"[{level}] {message}", color))
        if file_handle:
            file_handle.write(json.dumps(entry) + "\n")

    def _close():
        if file_handle:
            file_handle.close()

    return _log, _close


def process_text(text: str, log, router: FactRouter):
    sentences = split_sentences(text)
    timings = {name: 0.0 for name in PARSER_FUNCS}
    counts = {name: {"facts": 0, "opinions": 0} for name in PARSER_FUNCS}
    total_errors = 0

    for sent in sentences:
        opinion = is_opinion(sent)
        if opinion:
            log("INFO", f"Opinion detected: '{sent}'")
            opinion_record = {
                "type": "opinion",
                "fact": sent,
                "source": "parser_test_harness",
                "timestamp": datetime.now().isoformat(),
            }
            router.route_fact(opinion_record, category="opinions")

        routed = False
        for name, func in PARSER_FUNCS.items():
            start = time.perf_counter()
            try:
                log("INFO", f"Routing to {name} parser", sentence=sent)
                results = func(sent)
                elapsed = time.perf_counter() - start
                timings[name] += elapsed
                if results:
                    routed = True
                    counts[name]["facts"] += len(results)
                    if opinion:
                        counts[name]["opinions"] += 1
                    for rec in results:
                        rec.setdefault("timestamp", datetime.now().isoformat())
                        stored, path = router.route_fact(rec)
                        if stored:
                            log("INFO", f"{name} parser stored fact", sentence=sent, path=path)
                        else:
                            log("WARN", f"{name} parser produced duplicate fact", sentence=sent, path=path)
                    break
                else:
                    log("WARN", f"{name} parser returned no facts", sentence=sent)
            except Exception as exc:
                elapsed = time.perf_counter() - start
                timings[name] += elapsed
                log("ERROR", f"{name} parser exception: {exc}", sentence=sent)
                total_errors += 1
        if not routed:
            log("ERROR", f"No parser handled sentence", sentence=sent)
            total_errors += 1

    return timings, counts, total_errors


def main():
    parser = argparse.ArgumentParser(description="Unified parser test harness")
    parser.add_argument("text", nargs="?", help="Input text; if omitted read from stdin")
    parser.add_argument("--log", action="store_true", dest="log", help="Write debug log to file")
    args = parser.parse_args()

    input_text = args.text if args.text else sys.stdin.read()
    if not input_text:
        print("No input provided", file=sys.stderr)
        sys.exit(1)

    log, close_logger = make_logger(args.log)
    router = prepare_router()

    try:
        timings, counts, errors = process_text(input_text, log, router)
    finally:
        close_logger()

    print("\nParser statistics:")
    for name in PARSER_FUNCS:
        stats = counts[name]
        print(f"{name}: {stats['facts']} facts, {stats['opinions']} opinions, {timings[name]:.4f}s")

    if errors == 0:
        print(color_text("✅ All inputs parsed and routed successfully.", Colors.GREEN))
    else:
        print(color_text("❌ Some inputs failed routing or parsing. See logs above.", Colors.RED))


if __name__ == "__main__":
    main()
