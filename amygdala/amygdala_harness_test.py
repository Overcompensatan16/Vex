import json
import os
import sys
from amygdala import Amygdala, SomaticResponse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run_amygdala_harness() -> None:
    path = Amygdala().memory_path
    # Ensure clean start
    if os.path.exists(path):
        os.remove(path)
    amy = Amygdala(memory_path=path)
    test_fact = {
        "fact": "approaching fire",
        "tags": ["explosion"],
        "credibility": 0.9,
    }
    level = amy.assess_threat(test_fact)
    print(f"[Harness] Fear level: {level}")
    amy.react(level, test_fact)
    amy.react(level, test_fact)
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()
    assert len(lines) == 2, "fear events were not appended"
    print(f"[Harness] Memory events appended: {len(lines)}")


def run_somatic_response_harness() -> None:
    s = SomaticResponse()
    s.simulate_response("mild", ["tremor"])
    assert s.get_current_feelings() == ["tremor"]
    s.clear_response()
    assert s.get_current_feelings() == []
    print("[Harness] SomaticResponse cycle passed")


if __name__ == "__main__":
    run_amygdala_harness()
    run_somatic_response_harness()
