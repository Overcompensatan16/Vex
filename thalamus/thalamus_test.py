from datetime import datetime
from thalamus_module import ThalamusModule


class MockSignal:
    def __init__(self, source, tags=None, data=None):
        self.source = source
        self.tags = tags or []
        self.data = data or {}

    def as_dict(self):
        return {
            "source": self.source,
            "tags": self.tags,
            "data": self.data,
            "timestamp": datetime.now().isoformat(),
        }


def run_thalamus_tests():
    print("\n[ThalamusTest] Starting tests...\n")

    thalamus = ThalamusModule(audit_log_path="test_thalamus_log.jsonl")

    # Test 1: Neutral signal
    signal1 = MockSignal(source="sensor", tags=["misc"])
    result1 = thalamus.score_signal(signal1)
    assert result1.priority_metadata["decision"] == "defer", "❌ Should defer neutral signal"

    # Test 2: Pain signal
    signal2 = MockSignal(source="user", tags=["pain"])
    result2 = thalamus.score_signal(signal2)
    assert result2.priority_metadata["decision"] == "route", "❌ Should route pain signal"

    # Test 3: Hazard signal
    signal3 = MockSignal(source="user", tags=["hazard"])
    result3 = thalamus.score_signal(signal3)
    assert result3.priority_metadata["decision"] == "route", "❌ Should route hazard signal"

    print("[ThalamusTest] ✅ All tests passed.\n")

    # Optional: Print scored signal details
    for i, result in enumerate([result1, result2, result3], 1):
        print(
            f"[Test {i}] Decision: {result.priority_metadata['decision']} | "
            f"Score: {result.priority_metadata['priority_score']:.2f} | "
            f"Tags: {result.priority_metadata['salience_tags']}"
        )


if __name__ == "__main__":
    run_thalamus_tests()

