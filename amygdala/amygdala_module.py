from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Optional

from amygdala.somatic_response import SomaticResponse
from audit.audit_logger_factory import AuditLoggerFactory

try:  # optional import
    from limbic_system.limbic_system_module import LimbicSystem
except Exception:  # pragma: no cover - optional dependency
    LimbicSystem = Any  # type: ignore


class Amygdala:
    """Threat evaluation and fear learning subsystem."""

    def __init__(
        self,
        config_path: str = "amygdala/amygdala_config.json",
        memory_path: str = r"E:\\Amygdala\\fear_memory.jsonl",
        *,
        limbic: Optional[LimbicSystem] = None,
    ) -> None:
        self.config_path = config_path
        self.memory_path = memory_path
        self.somatic = SomaticResponse()
        self.limbic = limbic
        self.logger = AuditLoggerFactory("amygdala")
        self.config = self._load_config(config_path)
        self.innate_fears = set(self.config.get("innate_fears", []))
        self.trigger_tags = set(self.config.get("trigger_tags", []))
        self.reactions = self.config.get("fear_reactions", {})
        self.body_responses = self.config.get("body_responses", {})
        mem_dir = os.path.dirname(memory_path)
        if mem_dir:
            os.makedirs(mem_dir, exist_ok=True)
        if not os.path.exists(memory_path):
            open(memory_path, "a", encoding="utf-8").close()
        print("[Amygdala] Initialized.")

    def assess_threat(self, input_data: dict) -> str:
        """
        Evaluate the threat level based on tags and credibility.
        Returns: "none", "mild", "moderate", or "severe"
        """
        score = 0
        tags = input_data.get("tags", [])
        credibility = input_data.get("credibility", 0)

        if any(tag in self.trigger_tags for tag in tags):
            score += 2
        if any(tag in self.innate_fears for tag in tags):
            score += 3
        score += int(credibility * 2)

        if score >= 5:
            return "severe"
        elif score >= 3:
            return "moderate"
        elif score > 0:
            return "mild"
        return "none"

    # ------------------------------------------------------------------ utils --
    @staticmethod
    def _load_config(path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except FileNotFoundError:
            print(f"[Amygdala] Config missing at {path}. Using defaults.")
            return {}
        except json.JSONDecodeError as exc:
            print(f"[Amygdala] Config decode error: {exc}")
            return {}

    def _append_memory(self, entry: dict) -> None:
        with open(self.memory_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")

    def react(self, fear_level: str, context: dict | None = None) -> dict:
        """Trigger response chain for `fear_level`. Returns reaction details."""
        responses = self.body_responses.get(fear_level, [])
        self.somatic.simulate_response(fear_level, responses)
        actions = self.reactions.get(fear_level, [])
        event = {
            "trigger": context.get("fact") if context else None,
            "context": context.get("tags") if context else [],
            "intensity": fear_level,
            "reaction": actions,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reinforced": 1,
        }
        self.store_fear_experience(event)
        return {"actions": actions, "body": responses}

    # ---------------------------------------------------------------- memory --
    def store_fear_experience(self, event: dict) -> None:
        """Persist event to fear memory."""
        self._append_memory(event)
        self.log_fear_event(event)

    def log_fear_event(self, event: dict) -> None:
        """Record the fear event to the amygdala audit log."""
        self.logger.log_event("fear_event", event)

    def learn_new_fear(self, event: dict, outcome: str) -> None:
        """Add a new learned fear based on outcome."""
        if outcome == "negative":
            trigger = event.get("trigger")
            if trigger:
                self.trigger_tags.add(trigger)
                self.config.setdefault("trigger_tags", list(self.trigger_tags))
                with open(self.config_path, "w", encoding="utf-8") as fh:
                    json.dump(self.config, fh, indent=2)
                print(f"[Amygdala] Learned new fear trigger: {trigger}")

    # ---------------------------------------------------------------- decay --
    def decay_learned_fear(self, time_passed: float) -> None:
        """Reduce reinforcement count based on time."""
        events = self._load_memory()
        updated = []
        for ev in events:
            reinforced = ev.get("reinforced", 0)
            if reinforced > 0 and time_passed > 0:
                ev["reinforced"] = max(0, reinforced - 1)
            updated.append(ev)
        with open(self.memory_path, "w", encoding="utf-8") as fh:
            for ev in updated:
                fh.write(json.dumps(ev) + "\n")
