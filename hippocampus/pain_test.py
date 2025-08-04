from datetime import datetime, timezone
import json
from pain_detector import PainDetector

# Minimal mock hippocampus for testing


class MockHippocampus:
    def __init__(self):
        self.facts = []

    def store_record(self, record, category=None):
        self.facts.append(record)
        print(f"[MockHippocampus] Stored fact: {record['fact']} (priority: {record['priority_weight']})")


def run_pain_detector_tests():
    hippocampus = MockHippocampus()
    pain_detector = PainDetector(hippocampus)

    # Simulate test triggers
    print("\n[Test] Triggering synthetic pain event #1")
    pain_detector.trigger_pain("test synthetic pain trigger #1")

    print("\n[Test] Triggering synthetic pain event #2 with high urgency")
    pain_detector.trigger_pain("test synthetic pain trigger #2", priority_weight=1)

    # Display facts stored
    print("\n[Test] Final facts in hippocampus:")
    for fact in hippocampus.facts:
        print(json.dumps(fact, indent=2))

    # Check audit log (optional)
    print("\n[Test] Audit log entries:")
    for log_entry in pain_detector.log:
        print(json.dumps(log_entry, indent=2))


if __name__ == "__main__":
    run_pain_detector_tests()
