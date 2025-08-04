import json
import os
import random
import sys
import types
from pineal_gland.pineal_gland import get_circadian_scalar
from limbic_system.desire_engine import DesireEngine, DesireModulator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if "spacy" not in sys.modules:
    dummy_nlp = types.SimpleNamespace(__call__=lambda text: types.SimpleNamespace(sents=[]))
    sys.modules["spacy"] = types.SimpleNamespace(load=lambda name: dummy_nlp)
    sys.modules["spacy.cli"] = types.SimpleNamespace(download=lambda name: None)

if "pygetwindow" not in sys.modules:
    sys.modules["pygetwindow"] = types.SimpleNamespace()

if "pyautogui" not in sys.modules:
    sys.modules["pyautogui"] = types.SimpleNamespace()


def run_pineal_test() -> None:
    """Sample the circadian scalar at 4 hour increments."""
    print("[PinealTest] Circadian scalar across simulated day:")
    for hour in range(0, 24, 4):
        scalar = get_circadian_scalar(seconds=hour * 3600)
        print(f"  Hour {hour:02d}: {scalar:.2f}")


def run_desire_engine_test(samples: int = 3) -> None:
    """Generate a few example desires using varying modulators."""
    print("\n[DesireEngineTest] Generating desires:")
    for n in range(samples):
        pineal = [get_circadian_scalar(seconds=n * 3600)]
        personality = [random.random() for _ in range(4)]
        context = [random.random() for _ in range(3)]
        mod = DesireModulator(pineal, personality, context)
        signal = DesireEngine.generate_desire(mod)
        if signal:
            print(json.dumps(signal.as_dict(), indent=2))
        else:
            print("  Desire filtered")


if __name__ == "__main__":
    run_pineal_test()
    run_desire_engine_test()
