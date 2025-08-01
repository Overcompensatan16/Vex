from datetime import datetime, timezone
from audit.audit_logger_factory import AuditLoggerFactory
from cerebral_cortex.temporal_lobe.context_tracker import ContextTracker
from symbolic_signal import SymbolicSignal


class ThalamusModule:
    """Scores incoming SymbolicSignals for salience and routing."""

    def __init__(self, audit_log_path: str | None = None, context_size: int = 10):
        self.focus_mode = "neutral"
        self.threshold = 0.2  # Route only if score ≥ threshold
        self.logger = AuditLoggerFactory("thalamus", log_path=audit_log_path)
        self.context = ContextTracker(max_size=context_size)
        self._log_focus_update("Initialized with neutral focus.")

    # ─────────────────────────────────────────  Public  ──────────────────────────

    def score_signal(self, signal_obj: SymbolicSignal) -> SymbolicSignal:
        """Score a SymbolicSignal and annotate it with priority metadata."""
        obj = signal_obj.as_dict()

        salience_tags, base_score = self._get_salience(obj)
        adjustment = self._intralaminar_modulation(obj, base_score)
        priority_score = min(1.0, max(0.0, base_score + adjustment))

        focus_fit = "high" if self.focus_mode in salience_tags else "low"
        decision = "route" if priority_score >= self.threshold else "defer"

        metadata = {
            "priority_score": priority_score,
            "salience_tags": salience_tags,
            "focus_fit": focus_fit,
            "decision": decision,
            "reason": (
                f"Scored in {self.focus_mode} focus mode "
                f"with {len(salience_tags)} salience tag(s)."
            ),
        }

        log_entry = obj.copy()
        log_entry["priority_metadata"] = metadata
        self.logger.log_event("scored_signal", log_entry)
        self.context.add(log_entry)

        signal_obj.priority_metadata = metadata
        return signal_obj

    def update_focus_mode(self, new_focus: str, reason: str = "manual update") -> None:
        """Change the current salience focus mode."""
        self.focus_mode = new_focus
        self._log_focus_update(f"Focus mode set to '{new_focus}' (Reason: {reason})")

    def get_focus_state(self) -> dict:
        """Return current focus mode with timestamp."""
        return {
            "focus_mode": self.focus_mode,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ─────────────────────────────────────────  Internal  ─────────────────────────

    @staticmethod
    def _get_salience(obj: dict) -> tuple[list[str], float]:
        """Derive salience tags and base score from input signal."""
        salience_tags: list[str] = []
        score = 0.1  # base score

        if "hazard" in obj.get("tags", []):
            salience_tags.append("hazard")
            score += 0.4
        if "pain" in obj.get("tags", []):
            salience_tags.append("pain")
            score += 0.3
        if obj.get("source") == "user":
            score += 0.2

        return salience_tags, score

    def _intralaminar_modulation(self, obj: dict, current_priority: float) -> float:
        """Adjust score based on focus mode ↔ tag alignment."""
        adjustment = 0.0

        if self.focus_mode == "hazard_focus" and "hazard" in obj.get("tags", []):
            adjustment += 0.1
            self._log_focus_update("Intralaminar: hazard salience boosted (+0.1)")

        elif self.focus_mode == "math_focus" and "math" in obj.get("tags", []):
            adjustment += 0.05
            self._log_focus_update("Intralaminar: math salience boosted (+0.05)")

        return adjustment

    def _log_focus_update(self, message: str) -> None:
        """Helper to log focus-mode changes and intralaminar events."""
        entry = {
            "focus_update": message,
            "focus_mode": self.focus_mode,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.logger.log_event("focus_update", entry)
        print(f"[Thalamus] {message}")


__all__ = ["ThalamusModule"]
