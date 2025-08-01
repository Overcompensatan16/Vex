from datetime import datetime, timezone
import json
import os

from audit.audit_logger_factory import AuditLoggerFactory
from cerebral_cortex.temporal_lobe.language_reasoner import process_text
from cerebral_cortex.temporal_lobe.language_parser import parse_language
from cerebral_cortex.temporal_lobe.context_tracker import ContextTracker


class TemporalLobe:
    """Processes auditory facts into linguistic representations."""

    DEFAULT_CONFIG = {
        "context_size": 10,
        "audit_log_path": None,
        "context_store_path": None,
    }

    def __init__(self, config_path="cerebral_cortex/temporal_lobe/linguistic_config.json", hippocampus=None):
        self.config_path = config_path
        self.hippocampus = hippocampus

        self.config = {}
        self.context_size = None
        self.log_path = None
        self.context_store_path = None
        self.logger = None
        self.context = None

        self.reload_config()
        print("[TemporalLobe] Initialized.")

    def reload_config(self):
        """Reload configuration from ``self.config_path``."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
                print(f"[TemporalLobe] Config loaded from {self.config_path}")
            else:
                self.config = self.DEFAULT_CONFIG.copy()
                print(f"[TemporalLobe] Config file not found. Using defaults.")
        except Exception as e:
            print(f"[TemporalLobe] Failed to load config: {e}. Using defaults.")
            self.config = self.DEFAULT_CONFIG.copy()

        self.context_size = self.config.get("context_size", self.DEFAULT_CONFIG["context_size"])
        self.log_path = self.config.get("audit_log_path", self.DEFAULT_CONFIG["audit_log_path"])
        self.context_store_path = self.config.get("context_store_path")

        if self.log_path:
            self.logger = AuditLoggerFactory("temporal_lobe", log_path=self.log_path)
        else:
            self.logger = AuditLoggerFactory("temporal_lobe")
        self.context = ContextTracker(max_size=self.context_size)

    def process(self, auditory_fact):
        """Parse structured auditory facts into language structures."""

        text = ""
        if hasattr(auditory_fact, "data"):
            text = auditory_fact.data.get("text", "")
        elif isinstance(auditory_fact, str):
            text = auditory_fact.get("text") or auditory_fact.get("transcript") or ""

        self.logger.log_event("temporal_input", {"text": text})
        if text:
            self.context.add({"original": text, "timestamp": datetime.now(timezone.utc).isoformat()})

        if not text:
            result = {
                "original": text,
                "tokens": [],
                "analysis": [],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "temporal_lobe",
            }
            self.logger.log_event("temporal_output", result)
            self.context.add(result)
            return result

        try:
            tokens = parse_language(text)
        except Exception as e:
            tokens = {"tokens": []}
            self.logger.log_error("parse_language_error", str(e))

        try:
            analysis = process_text(text)
        except Exception as e:
            analysis = []
            self.logger.log_error("process_text_error", str(e))

        result = {
            "original": text,
            "tokens": tokens.get("tokens", []),
            "analysis": analysis,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "temporal_lobe",
        }

        self.context.add(result)
        self.logger.log_event("temporal_output", result)

        if self.hippocampus:
            try:
                record = {
                    "fact": text,
                    "type": "linguistic_analysis",
                    "tarot": {"trump": None, "suit": "Swords"},
                    "source": "temporal_lobe",
                    "credibility": 1.0,
                    "tags": ["linguistic"],
                }
                self.hippocampus.store_record(record, category="linguistic")
            except Exception as e:
                self.logger.log_error("hippocampus_store_failed", str(e))

        if self.context_store_path:
            try:
                with open(self.context_store_path, "w", encoding="utf-8") as f:
                    json.dump(self.context.recent(), f, indent=2)
            except Exception as e:
                self.logger.log_error("context_store_failed", str(e))

        return result

    def get_recent_context(self):
        """Return a list of recently processed entries."""
        return self.context.recent()


__all__ = ["TemporalLobe"]
