import os
import sys
import types
import warnings
import pytest

sys.modules.setdefault('spacy', types.ModuleType('spacy'))
sys.modules['spacy'].load = lambda *args, **kwargs: None
sys.modules.setdefault('pygetwindow', types.ModuleType('pygetwindow'))
sys.modules.setdefault('pyautogui', types.ModuleType('pyautogui'))
temporal_stub = types.ModuleType('cerebral_cortex.temporal_lobe')
chemistry_stub = types.ModuleType('cerebral_cortex.temporal_lobe.chemistry_parser')
chemistry_stub.parse_chemistry_text = lambda text: []
temporal_stub.chemistry_parser = chemistry_stub
temporal_stub.__path__ = []
sys.modules.setdefault('cerebral_cortex.temporal_lobe', temporal_stub)
sys.modules.setdefault('cerebral_cortex.temporal_lobe.chemistry_parser', chemistry_stub)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from cerebral_cortex.fact_generator.fact_generator import generate_facts


def _print_warnings(warns):
    for w in warns:
        print(f"Warning: {w.message} ({w.category.__name__}) from {w.filename}:{w.lineno}")


def test_generate_facts_basic():
    text = "Water boils at 100 degrees. Hydrogen is an element."
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        facts = generate_facts(text, source='language')
    _print_warnings(w)
    assert len(facts) == 2


def test_generate_facts_arxiv_type_passthrough():
    text = "We propose a new AI method."
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        facts = generate_facts(text, source='arxiv', source_type='cs.AI')
    _print_warnings(w)
    assert facts[0]['type'] == 'cs.AI'


def test_generate_facts_wikipedia_type_override():
    text = "The Roman Empire was vast."
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        facts = generate_facts(text, source='wiki', source_type='history.rome')
    _print_warnings(w)
    assert facts[0]['type'] == 'history.rome'


def test_records_from_screen_reasoning_logs_normalization(monkeypatch):
    from cerebral_cortex.fact_generator import fact_generator

    captured = {}

    def fake_log_event(event_type, data):
        captured['event_type'] = event_type
        captured['data'] = data

    monkeypatch.setattr(fact_generator.LOGGER, 'log_event', fake_log_event)

    reasoning = {"screen_analysis": [{"original": "Teh cat", "analysis": []}]}
    fact_generator.records_from_screen_reasoning(reasoning)

    assert captured['event_type'] == 'transformer_normalization'
    assert captured['data']['message'] == 'Transformer normalization applied to OCR/STT input'
    assert captured['data']['tag'] == 'ocr'
    assert captured['data']['source'] == 'ocr_reasoner'
