import json
import os
import sys
from core_personality import CorePersonality

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run_harness() -> None:
    cp = CorePersonality()
    shaped = cp.shape_output("Hello from harness", confidence=0.95)
    about = cp.about_me()
    print(json.dumps(shaped, indent=2))
    print("\n[Harness] About me:\n" + about)


if __name__ == "__main__":
    run_harness()
