import sys
import os
import types

# Minimal spaCy stub so LimbicSystem imports without heavy dependency
if 'spacy' not in sys.modules:
    dummy_nlp = types.SimpleNamespace(__call__=lambda text: types.SimpleNamespace(sents=[]))
    sys.modules['spacy'] = types.SimpleNamespace(load=lambda name: dummy_nlp)
    sys.modules['spacy.cli'] = types.SimpleNamespace(download=lambda name: None)
if 'pygetwindow' not in sys.modules:
    sys.modules['pygetwindow'] = types.SimpleNamespace()
if 'pyautogui' not in sys.modules:
    sys.modules['pyautogui'] = types.SimpleNamespace()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class MockRouter:
    def __init__(self):
        self.records = []

    def route_fact(self, record, category=None):
        self.records.append((record, category))


def run_limbic_memory_test():
    from limbic_system.limbic_system_module import LimbicSystem
    from symbolic_signal import SymbolicSignal

    router = MockRouter()
    system = LimbicSystem(memory_router=router)
    sig = SymbolicSignal("test stimulus", "text", "tester", ["joy"])
    system.evaluate_signal(sig)

    assert router.records, "Memory router should receive a record"
    rec, cat = router.records[0]
    print(f"✅ Routed category: {cat}")
    print(f"✅ Record fact: {rec['fact']}")


if __name__ == "__main__":
    run_limbic_memory_test()
