import json
import os
import sys
import types
from limbic_system.limbic_system_module import LimbicSystem
from symbolic_signal import SymbolicSignal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Minimal spaCy stub so LimbicSystem imports without heavy dependency
if 'spacy' not in sys.modules:
    dummy_nlp = types.SimpleNamespace(__call__=lambda text: types.SimpleNamespace(sents=[]))
    sys.modules['spacy'] = types.SimpleNamespace(load=lambda name: dummy_nlp)
    sys.modules['spacy.cli'] = types.SimpleNamespace(download=lambda name: None)
if 'pygetwindow' not in sys.modules:
    sys.modules['pygetwindow'] = types.SimpleNamespace()
if 'pyautogui' not in sys.modules:
    sys.modules['pyautogui'] = types.SimpleNamespace()


def run_harness() -> None:
    system = LimbicSystem()

    test_signals = [
        SymbolicSignal("Minor pain detected", "text", "system", ["pain"]),
        SymbolicSignal("Hazard approaching", "text", "sensor", ["hazard"]),
        SymbolicSignal("User compliment", "text", "user", ["joy", "Keter"]),
    ]

    for sig in test_signals:
        result = system.evaluate_signal(sig)
        print(json.dumps(result, indent=2))

    print("\n[Harness] Context entries:")
    for entry in system.context.recent():
        print(json.dumps(entry, indent=2))


if __name__ == "__main__":
    run_harness()
