import os
import sys
import types
from cerebral_cortex.fact_generator.fact_generator import generate_facts
from cerebral_cortex.source_handlers.external_loaders.arxiv_handler import CODE_TO_TYPE
from cerebral_cortex.source_handlers.external_loaders.wiki_handler import tag_facts

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
)


fake_spacy = types.ModuleType("spacy")
fake_spacy.load = lambda *args, **kwargs: None
sys.modules.setdefault("spacy", fake_spacy)
sys.modules.setdefault("pygetwindow", types.ModuleType("pygetwindow"))
sys.modules.setdefault("pyautogui", types.ModuleType("pyautogui"))


def test_generate_facts_arxiv_type_mapping():
    text = "We propose a new AI method."
    facts = generate_facts(text, source="arxiv", source_type="cs.AI")
    assert facts[0]["type"] == CODE_TO_TYPE["cs.AI"]


def test_generate_facts_wikipedia_type_override():
    text = "The Roman Empire was vast."
    facts = generate_facts(text, source="wiki", source_type="history.rome")
    assert facts[0]["type"] == "history.rome"


def test_tag_facts_classifies_science():
    text = "Chemical reactions are part of science."
    facts = generate_facts(text, source="wiki")
    tag_facts("science_article.txt", text, facts)
    assert facts[0]["type"] == "wiki.scientific"
    assert facts[0]["source"] == "wikipedia"
