import pygetwindow as gw
from datetime import datetime, timezone

from basal_ganglia.window_intent_gate import gate_window_switch
from prefrontal_cortex.window_switcher import perform_window_switch


def decide(user_input: str):
    """Basic string analysis and symbolic intent routing"""
    conclusions = []

    cleaned_input = user_input.strip()
    if not cleaned_input:
        return ["⚠️ Empty input received."]

    if cleaned_input.endswith('='):
        cleaned_input = cleaned_input[:-1].strip()

    # Intent detection: rudimentary placeholder
    if cleaned_input.lower().startswith("switch "):
        label = cleaned_input.split(" ", 1)[-1].strip()
        intent = {"intent": "switch_to", "target_label": label}
        gate = gate_window_switch(intent)

        if gate["status"] == "approved":
            switch_result = perform_window_switch(gate["matched_window"])
            if switch_result["status"] == "success":
                conclusions.append(f"🪟 Switched to: {switch_result['window_title']}")
            else:
                conclusions.append("❌ Switch failed: " + switch_result.get("error", "Unknown"))
        else:
            conclusions.append("🚫 Switch inhibited: No matching window.")

    elif any(char.isdigit() for char in cleaned_input) and any(op in cleaned_input for op in "+-*/"):
        try:
            result = eval(cleaned_input, {"__builtins__": {}})
            conclusions.append(f"🧠 Math result: {result}")
        except Exception as e:
            conclusions.append(f"❌ Math error: {e}")

    elif any(term in cleaned_input.lower() for term in ("fire", "pain", "hazard")):
        conclusions.append("⚠️ Hazard or pain signal detected. Routing to detection modules...")

    else:
        conclusions.append(f"💬 Processed input: {cleaned_input}")

    return conclusions


class PrefrontalCortexModule:
    def __init__(self, hippocampus=None, hazard_reasoner=None, math_reasoner=None, math_decision=None):
        self.hippocampus = hippocampus
        self.hazard_reasoner = hazard_reasoner
        self.math_reasoner = math_reasoner
        self.chat_module = chat_module
        self.math_decision = math_decision
        self.actions = []
        print("[PrefrontalCortexModule] Initialized.")

    def process_input(self, user_input: str):
        """Routes input through all modules and returns conclusions"""
        conclusions = []

        if self.math_reasoner and any(char.isdigit() for char in user_input):
            math_results = self.math_reasoner.infer(user_input)
            if math_results:
                conclusions.extend([f"Math: {c}" for c in math_results])

        if self.hazard_reasoner:
            hazard_results = self.hazard_reasoner.infer()
            if hazard_results:
                conclusions.extend([f"Hazard: {c}" for c in hazard_results])

        if not conclusions and self.chat_module:
            chat_response = self.chat_module.handle_input(user_input)
            conclusions.append(f"Chat: {chat_response}")

        self.execute(conclusions)
        return conclusions

    def execute(self, conclusions):
        """Final action emitter"""
        for conclusion in conclusions:
            if "ALERT" in conclusion or "ACTION" in conclusion:
                self.actions.append(conclusion)
                print(conclusion)

        print(f"[PrefrontalCortexModule] Final conclusions: {conclusions}")
