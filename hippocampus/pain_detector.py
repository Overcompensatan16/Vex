import json
from datetime import datetime, timezone


class PainDetector:
    def __init__(self, hippocampus, config=None, audit_log_path="pain_audit_log.jsonl"):
        self.hippocampus = hippocampus
        self.config = config or {
            "pain_thresholds": {
                "default_priority_weight": 5,
                "max_pain_priority": 0,
                "min_pain_priority": 10
            }
        }
        self.audit_log_path = audit_log_path
        self.log = []

    def trigger_pain(self, cause_text, trigger_type="generic", priority_weight=None):
        priority_map = self.config.get("pain_thresholds", {})
        computed_priority = priority_map.get(
            f"{trigger_type}_priority",
            priority_map.get("default_priority_weight", 5)
        )

        if priority_weight is not None:
            computed_priority = priority_weight

        computed_priority = max(
            priority_map.get("max_pain_priority", 0),
            min(computed_priority, priority_map.get("min_pain_priority", 10))
        )

        fact_text = f"Pain triggered by {cause_text}"
        pain_fact = {
            "fact": fact_text,
            "type": "pain",
            "tarot": {"trump": "The Tower", "suit": "Cups"},
            "source": "pain_detector",
            "credibility": 1.0,
            "tags": ["auto_injected"],
            "connections": [],
            "priority_weight": computed_priority,
            "reversal": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self.hippocampus.store_record(pain_fact, category="pain")

        log_entry = {
            "fact": fact_text,
            "cause": cause_text,
            "priority_weight": computed_priority,
            "timestamp": pain_fact["timestamp"]
        }

        self.log.append(log_entry)
        self._write_audit_log(log_entry)

        print(f"[PainDetector] Pain fact injected: {fact_text}")

    def _write_audit_log(self, entry):
        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"[PainDetector] Failed to write audit log: {e}")
