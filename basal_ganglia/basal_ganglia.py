import json
from datetime import datetime, timezone


class BasalGanglia:
    def __init__(self, audit_logger=None, config=None):
        self.audit_logger = audit_logger
        self.config = config or {}
        self.focus_mode = "neutral"
        self.dopamine_level = 0.5  # baseline dopamine
        self.action_threshold = 0.6  # base approval threshold

    def propose_action(self, action_obj):
        # Striatum layer: intake + basic filtering
        striatum_out = self._striatum_filter(action_obj)

        # STN layer: add inhibitory influence
        stn_mod = self._stn_influence(striatum_out)

        # SN layer: dopaminergic modulation
        sn_mod = self._sn_modulation(striatum_out, stn_mod)

        # GPi: final decision
        decision = self._gpi_decision(striatum_out, stn_mod, sn_mod)

        # Log the decision
        self._log_decision(action_obj, decision, striatum_out, stn_mod, sn_mod)

        return {
            "action": action_obj,
            "decision": decision,
            "focus_mode": self.focus_mode,
            "striatum": striatum_out,
            "stn_mod": stn_mod,
            "sn_mod": sn_mod
        }

    @staticmethod
    def _striatum_filter(action_obj):
        print("[DEBUG] Raw action_obj passed to striatum_filter:", action_obj)
        return {
            "confidence": float(action_obj.get("confidence", 0.0)),
            "valence": float(action_obj.get("motivational_valence", 0.0)),
            "tone_tag": action_obj.get("tone_tag"),
            "salience": action_obj.get("salience"),
        }

    @staticmethod
    def _stn_influence(striatum_out):
        # Example: inhibit more if moral tension or pain
        if striatum_out["salience"] == "moral_tension":
            return 0.2
        if striatum_out["salience"] == "pain":
            return 0.3
        return 0.0

    def _sn_modulation(self, striatum_out, stn_mod):
        dopamine_boost = (self.dopamine_level - 0.5) * 0.2
        return dopamine_boost - stn_mod

    def _gpi_decision(self, striatum_out, stn_mod, sn_mod):
        score = striatum_out["confidence"] + sn_mod - stn_mod
        if score >= self.action_threshold:
            return {"status": "approved", "final_score": round(score, 3)}
        elif score >= (self.action_threshold - 0.1):
            return {"status": "deferred", "final_score": round(score, 3)}
        else:
            return {"status": "inhibited", "final_score": round(score, 3)}

    def _log_decision(self, action_obj, decision, striatum_out, stn_mod, sn_mod):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action_obj,
            "decision": decision,
            "focus_mode": self.focus_mode,
            "striatum": striatum_out,
            "stn_mod": stn_mod,
            "sn_mod": sn_mod
        }
        if self.audit_logger:
            self.audit_logger.log_output(entry)
        else:
            print(f"[BasalGanglia] {json.dumps(entry, indent=2)}")
