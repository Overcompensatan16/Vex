# prefrontal_cortex/action_gate.py

from cerebral_cortex.optic_nerve.vision_reasoner import reason_screen
from cerebral_cortex.optic_nerve.vision_parser import parse_screen
from basal_ganglia.basal_ganglia import BasalGanglia
from audit.audit_logger import AuditLogger  # <-- Updated to class


class DeferredActionQueue:
    def __init__(self, logger: AuditLogger):
        self.queue = []
        self.audit_logger = logger

    def add(self, action):
        print(f"[Queue] Deferring action: {action['intent']} ({action['confidence']:.2f})")
        self.audit_logger.record("DeferredAction", f"Deferred intent: {action['intent']}", data=action)
        self.queue.append(action)

    def flush(self):
        print("[Queue] Flushing deferred actions...")
        self.audit_logger.record("DeferredAction", "Flushing deferred queue", data=self.queue)
        for action in self.queue:
            print(f" - {action['intent']} (conf: {action['confidence']:.2f})")
        return self.queue.copy()

    def clear(self):
        self.audit_logger.record("DeferredAction", "Clearing deferred queue")
        self.queue.clear()


# Create logger instance
audit_logger = AuditLogger()

# Pass logger to BasalGanglia and queue
basal_ganglia = BasalGanglia(audit_logger=audit_logger)
deferred_queue = DeferredActionQueue(logger=audit_logger)


def gate_screen_actions(region=None, allow_override=False):
    print("[ActionGate] Parsing screen...")
    audit_logger.record("ActionGate", "Parsing screen", data={"region": region})
    signal = parse_screen(region=region)
    parsed = signal.data if hasattr(signal, "data") else signal

    print("[ActionGate] Reasoning over screen...")
    audit_logger.record("ActionGate", "Reasoning over parsed screen")
    symbolic = reason_screen(parsed)
    symbolic_blocks = symbolic.get("interpreted_blocks", symbolic)

    gated_results = []

    print("[ActionGate] Evaluating intent candidates...")
    for block in symbolic_blocks:
        if 'intent' not in block or 'primary_action' not in block:
            continue

        action_obj = {
            "intent": block["intent"],
            "action": block["primary_action"],
            "confidence": block.get("priority", 0.0),
            "motivational_valence": block.get("valence", 0.0),
            "tone_tag": block.get("tone_tag"),
            "salience": block.get("salience"),
        }

        audit_logger.record("ActionGate", f"Evaluating intent: {action_obj['intent']}", data=action_obj)
        decision = basal_ganglia.propose_action(action_obj)
        status = decision['decision']['status']

        if status == "deferred":
            deferred_queue.add(action_obj)
        elif status == "inhibited" and allow_override:
            print(f"[Override] Forcing inhibited action: {action_obj['intent']}")
            audit_logger.record("Override", f"Forcing inhibited action: {action_obj['intent']}", data=decision)
            decision['decision']['status'] = "forced"
            gated_results.append(decision)
        elif status == "approved":
            gated_results.append(decision)
            audit_logger.record("ActionGate", f"Approved action: {action_obj['intent']}", data=decision)

    return gated_results


def flush_deferred_actions():
    deferred = deferred_queue.flush()
    deferred_queue.clear()
    return deferred


if __name__ == "__main__":
    results = gate_screen_actions(allow_override=True)
    print("\n--- Final Results ---")
    for r in results:
        print(f"[Result] {r['decision']['status']}: {r['action']['intent']} ({r['decision']['final_score']:.2f})")

    print("\n--- Deferred Queue ---")
    flush_deferred_actions()
