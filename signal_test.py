import sys
import os
import types
import importlib.util

# Minimal spaCy stub so LimbicSystem imports without heavy dependency
if 'spacy' not in sys.modules:
    dummy_nlp = types.SimpleNamespace(__call__=lambda text: types.SimpleNamespace(sents=[]))
    sys.modules['spacy'] = types.SimpleNamespace(load=lambda name: dummy_nlp)
    sys.modules['spacy.cli'] = types.SimpleNamespace(download=lambda name: None)
if 'pygetwindow' not in sys.modules:
    sys.modules['pygetwindow'] = types.SimpleNamespace()
if 'pyautogui' not in sys.modules:
    sys.modules['pyautogui'] = types.SimpleNamespace()

# ✅ Manually load SymbolicSignal to avoid shadowing from symbolic_signal/ directory
signal_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "symbolic_signal.py"))
spec = importlib.util.spec_from_file_location("symbolic_signal_file", signal_path)
symbolic_signal_file = importlib.util.module_from_spec(spec)
spec.loader.exec_module(symbolic_signal_file)

SymbolicSignal = symbolic_signal_file.SymbolicSignal

from limbic_system.limbic_system_module import LimbicSystem

records: list[dict] = []

def mock_router(record, category=None):  # category kept for compatibility
    records.append((record, category))
    return True, "memory.jsonl"

def run_limbic_memory_test():
    system = LimbicSystem(memory_router=mock_router)
    sig = SymbolicSignal("test stimulus", "text", "tester", ["joy"])
    system.evaluate_signal(sig)

    assert records, "Memory router should receive a record"
    rec, cat = records[0]
    print(f"✅ Routed category: {cat}")
    print(f"✅ Record fact: {rec['fact']}")

if __name__ == "__main__":
    run_limbic_memory_test()
