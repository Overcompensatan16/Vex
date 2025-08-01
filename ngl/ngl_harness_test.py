import os
import sys
import types
from ngl.natural_language_generator import generate_natural_phrase
from ngl.fact_extractor import parse_fact_from_sentence
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Stub heavy dependencies for quick harness execution
if "spacy" not in sys.modules:
    dummy_nlp = types.SimpleNamespace(__call__=lambda text: types.SimpleNamespace(sents=[]))
    sys.modules["spacy"] = types.SimpleNamespace(load=lambda name: dummy_nlp)
    sys.modules["spacy.cli"] = types.SimpleNamespace(download=lambda name: None)
if "pygetwindow" not in sys.modules:
    sys.modules["pygetwindow"] = types.SimpleNamespace()
if "pyautogui" not in sys.modules:
    sys.modules["pyautogui"] = types.SimpleNamespace()


def run_harness() -> None:
    """Run a simple NGL demonstration using parsed input."""
    input_phrase = "Did you know water is essential for life?"
    fact = parse_fact_from_sentence(input_phrase)

    if not fact:
        print("[NGLHarness] Failed to parse fact.")
        return

    tone_info = {
        "emotion": "curious",
        "tone": "informative",
        "personality_style": "scholarly",
    }

    result = generate_natural_phrase(fact, tone_info)

    response = result if isinstance(result, str) else result.get("phrase", "")
    tags = result.get("tags", []) if isinstance(result, dict) else []

    print("[NGLHarness] Input:", input_phrase)
    print("[NGLHarness] Response:", response)
    print("[NGLHarness] Tags:", tags)


if __name__ == "__main__":
    run_harness()
