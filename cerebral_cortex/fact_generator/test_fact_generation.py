import os
import sys
import types
import warnings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from cerebral_cortex.fact_generator.fact_generator import generate_facts

fake_spacy = types.ModuleType('spacy')
fake_spacy.load = lambda *args, **kwargs: None
sys.modules.setdefault('spacy', fake_spacy)
sys.modules.setdefault('pygetwindow', types.ModuleType('pygetwindow'))
sys.modules.setdefault('pyautogui', types.ModuleType('pyautogui'))

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