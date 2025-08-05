#!/usr/bin/env python3
"""CLI test harness for subject-specific parsers."""

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

# --- Basic config ---
BASE_MEMORY_PATH = os.path.normpath(r"E:\AI_Memory_Stores")
FACT_GEN_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "cerebral_cortex", "fact_generator", "fact_generator.py")
)
SUBJECT_PARSER_DIR = os.path.normpath(
    r"D:\AI DEVELOPMENT\AI Development\hyper_ai_core\cerebral_cortex\temporal_lobe\subject_parsers"
)

# --- Stub for colored output (can be replaced with rich or termcolor) ---
class Colors:
    GREEN = ""
    YELLOW = ""
    RED = ""
    RESET = ""

def color_text(text, color):
    return text

# --- Load is_opinion function from AST-only ---
with open(FACT_GEN_PATH, "r", encoding="utf-8") as fact_file:
    tree = ast.parse(fact_file.read(), FACT_GEN_PATH)

is_opinion_node = next(
    (n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "is_opinion"),
    None
)
if is_opinion_node is None:
    raise RuntimeError(f"'is_opinion' function not found in {FACT_GEN_PATH}")

module = ast.Module(body=[is_opinion_node], type_ignores=[])
global_ns: Dict[str, object] = {}
exec(compile(module, FACT_GEN_PATH, "exec"), global_ns)

_is_opinion_func = global_ns.get("is_opinion")
if not callable(_is_opinion_func):
    raise TypeError(f"'is_opinion' from {FACT_GEN_PATH} is not callable: {type(_is_opinion_func)}")

# --- Parser loader ---
def _load_parser(module_name: str, func_name: str):
    path = os.path.join(SUBJECT_PARSER_DIR, f"{module_name}.py")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Parser module not found: {path}")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec for {module_name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    func = getattr(mod, func_name, None)
    if not callable(func):
        raise TypeError(f"{module_name}.{func_name} is not callable")
    return func

# --- Load all subject parsers ---
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

PARSER_FUNCS = {
    "bio": parse_bio_text,
    "chemistry": parse_chemistry_text,
    "conservation": parse_conservation_text,
    "cs": parse_cs_text,
    "econ": parse_econ_text,
    "eess": parse_eess_text,
    "game_theory": parse_game_theory_text,
    "geo": parse_geo_text,
    "history": parse_history_text,
    "law": parse_law_text,
    "math": parse_math_text,
    "philosophy": parse_philosophy_text,
    "physics": parse_physics_text,
    "stats": parse_stats_text,
}

# --- Dummy router factory ---
def prepare_router():
    return FactRouter(memory_path=BASE_MEMORY_PATH)

# --- Sentence splitter ---
def split_sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\\s+", text) if s.strip()]

# --- Logger factory ---
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

# --- Core processing ---
def process_text(text: str, log, router: FactRouter) -> Tuple[Dict[str, float], Dict[str, Dict[str, int]], int, List[str]]:
    sentences = split_sentences(text)
    print("DEBUG sentences:", sentences)

    timings = {name: 0.0 for name in PARSER_FUNCS}
    counts = {name: {"facts": 0, "opinions": 0} for name in PARSER_FUNCS}
    total_errors = 0

    for sent in sentences:
        opinion = _is_opinion_func(sent)
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

    return timings, counts, total_errors, sentences

# --- CLI entrypoint ---
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
        timings, counts, errors, sentences = process_text(input_text, log, router)
    finally:
        close_logger()

    results_file = os.path.normpath(os.path.join(BASE_MEMORY_PATH, "parser_test_results.jsonl"))
    process_file = os.path.normpath(os.path.join(BASE_MEMORY_PATH, "parser_test_process.jsonl"))
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    with open(results_file, "a", encoding="utf-8") as rf:
        rf.write(json.dumps({"timestamp": datetime.now().isoformat(), "timings": timings, "counts": counts, "errors": errors}) + "\n")
    with open(process_file, "a", encoding="utf-8") as pf:
        pf.write(json.dumps({"timestamp": datetime.now().isoformat(), "input": input_text, "sentences": sentences}) + "\n")

    print("\nParser statistics:")
    for name in PARSER_FUNCS:
        stats = counts[name]
        print(f"{name}: {stats['facts']} facts, {stats['opinions']} opinions, {timings[name]:.4f}s")

    if errors == 0:
        print(color_text("\u2705 All inputs parsed and routed successfully.", Colors.GREEN))
    else:
        print(color_text("\u274C Some inputs failed routing or parsing. See logs above.", Colors.RED))

if __name__ == "__main__":
    main()
