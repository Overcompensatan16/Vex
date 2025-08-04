import importlib.util
from pathlib import Path

module_path = (
    Path(__file__).resolve().parents[1]
    / "cerebral_cortex"
    / "temporal_lobe"
    / "subject_parsers"
    / "psychology_parser.py"
)
spec = importlib.util.spec_from_file_location("psychology_parser", module_path)
psychology_parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(psychology_parser)
parse_psychology_text = psychology_parser.parse_psychology_text


def test_mental_disorder_pattern():
    text = "Schizophrenia is a mental disorder characterized by hallucinations and delusions."
    results = parse_psychology_text(text)
    assert results[0]["subtype"] == "mental_disorder"
    assert results[0]["disorder"].lower() == "schizophrenia"
    assert "hallucinations" in results[0]["description"].lower()


def test_cognitive_keyword_detection():
    text = "Memory and attention are crucial in cognitive psychology."
    results = parse_psychology_text(text)
    assert results[0]["subtype"] == "cognitive_term"
    assert "memory" in results[0]["terms"]
