# ===== reasoning.py =====
from hippocampus.hazard_rules import RULES


class Reasoner:
    def __init__(self, memory, reasoning_mode="generalized"):
        self.memory = memory
        self.log = []

        # Filter rules by mode
        self.rules = sorted(
            [rule for rule in RULES if f"mode:{reasoning_mode}" in rule["tags"]],
            key=lambda r: r["priority"]
        )

        print(f"[Reasoner] Loaded {len(self.rules)} rules for mode: {reasoning_mode}")

    def infer(self):
        facts = set(f["fact"] for f in self.memory.recall())
        conclusions = set()
        queue = list(facts)

        while queue:
            current_fact = queue.pop(0)
            for rule in self.rules:
                if all(cond in facts for cond in rule["conditions"]):
                    conclusion = rule["conclusion"]
                    if conclusion not in conclusions:
                        conclusions.add(conclusion)
                        queue.append(conclusion)
                        facts.add(conclusion)
                        # Log the rule firing
                        self.log.append({
                            "rule": rule["name"],
                            "conditions_met": rule["conditions"],
                            "conclusion": conclusion
                        })

        return list(conclusions)

    def print_log(self):
        if not self.log:
            print("No reasoning steps logged.")
        else:
            print("Reasoning log:")
            for entry in self.log:
                print(f"Rule: {entry['rule']} | Conditions met: {entry['conditions_met']} | Conclusion: {entry['conclusion']}")
