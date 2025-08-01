from hippocampus.hazard_rules import get_hazard_rules
from datetime import datetime


class HazardReasoner:
    def __init__(self, memory, reasoning_mode="generalized"):
        self.memory = memory
        self.log = []
        self.reasoning_mode = reasoning_mode
        self.rules = get_hazard_rules()
        print(f"[HazardReasoner] Loaded {len(self.rules)} rules.")

    def infer(self):
        query_tags = ["trump:TheStar", "suit:Hazard"]
        facts = self.memory.query_facts(tags=query_tags, min_credibility=0.0)

        conclusions = []
        for rule in self.rules:
            if f"mode:{self.reasoning_mode}" not in rule["tags"]:
                continue

            all_conditions_met = True
            for cond in rule["conditions"]:
                if "=" in cond:
                    key, value = cond.split("=", 1)
                    found_match = False
                    for fact in facts:
                        if f"{key}={value}" == fact.get("fact"):
                            found_match = True
                            break
                    if not found_match:
                        all_conditions_met = False
                        break
                else:
                    if not any(f["fact"] == cond for f in facts):
                        all_conditions_met = False
                        break

            if all_conditions_met:
                if rule["conclusion"] not in conclusions:
                    conclusions.append(rule["conclusion"])
                    self.log.append({
                        "rule": rule["name"],
                        "conclusion": rule["conclusion"],
                        "timestamp": datetime.now().isoformat()
                    })
        record = {
            "fact": rule["conclusion"],
            "type": "hazard",
            "tarot": {"trump": "The Tower", "suit": "Wands"},
            "source": "hazard_reasoner",
            "credibility": 1.0,
            "tags": ["conclusion"],
            "timestamp": datetime.now().isoformat(),
        }
        self.memory.store_record(record, category="pain")

    def print_log(self):
        if not self.log:
            print("[HazardReasoner] No log entries.")
        else:
            print("[HazardReasoner] Reasoning log:")
            for entry in self.log:
                print(entry)
