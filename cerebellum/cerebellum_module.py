import datetime
import json
import os


class Cerebellum:
    def __init__(self, config):
        self.config = config
        print("[Cerebellum] Initialized.")

    def finalize_output(self, action_result):
        now = datetime.datetime.now(datetime.timezone.utc)

        # Extract important fields safely
        action = action_result.get("action", {})
        decision = action_result.get("decision", {})
        raw_input = action_result.get("raw_input", "N/A")
        conclusion = action.get("conclusion", "No conclusion provided")

        # Build the smoothed_output field from decision
        smoothed_output = {
            "status": decision.get("status", "approved") if isinstance(decision, dict) else decision,
            "final_score": decision.get("final_score", 1.0) if isinstance(decision, dict) else 1.0,
        }

        # Create optional timing and body movement corrections
        timing_adjustments = {
            "utterance_delay": self.config.get("utterance_delay", 0.1)
        }

        vr_body_balance = [
            {"axis": "pitch", "correction": 0.01},
            {"axis": "roll", "correction": -0.005}
        ]

        # Create the final_output dictionary
        final_output = {
            "timestamp": now.isoformat(),
            "finalized": True,
            "smoothed_output": smoothed_output,
            "requery_triggered": False,
            "requery_reason": None,
            "timing_adjustments_applied": timing_adjustments,
            "vr_body_balance_corrections": vr_body_balance,
            "raw_input": raw_input,
            "conclusion": conclusion,
            "action": action,
            "decision": decision
        }

        return final_output

    def execute_action(self, action_result):
        finalized = self.finalize_output(action_result)
        print("[Cerebellum] Finalized Action Output:")
        print(json.dumps(finalized, indent=2))
        return finalized


# If you're running the cerebellum config from a file
if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), 'cerebellum_config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        cerebellum = Cerebellum(config_data)
        print("[Cerebellum] Loaded config from cerebellum/cerebellum_config.json")
    else:
        print("[Cerebellum] Config not found.")
