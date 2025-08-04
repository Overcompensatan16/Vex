import json
import os
from datetime import datetime, timezone, timedelta


DEFAULT_CONFIG = {
    "max_entries": 1000,
    "retain_days": 30,
}


class AuditLoggerFactory:
    """Create standardized audit loggers per module."""

    def __init__(
        self,
        module_name: str,
        log_dir: str = "AI_Audit",
        log_path: str | None = None,
        config: dict | None = None,
        config_path: str | None = None,
    ):
        self.module_name = module_name
        self.log_dir = os.path.join(log_dir, module_name)
        os.makedirs(self.log_dir, exist_ok=True)

        self.config = DEFAULT_CONFIG.copy()
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self.config.update(json.load(f))
            except Exception:
                pass
        if config:
            self.config.update(config)

        if log_path:
            log_dirname = os.path.dirname(log_path) or "."
            os.makedirs(log_dirname, exist_ok=True)
            self.log_path = log_path
        else:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            self.log_path = os.path.join(self.log_dir, f"{ts}.jsonl")
        self.entry_count = 0

    def log_event(self, event_type: str, data: dict):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "data": data,
        }
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        self.entry_count += 1
        self._prune_if_needed()

    def log_error(self, error_type: str, message: str):
        self.log_event(f"error:{error_type}", {"message": message})

    def log_warning(self, warning_type: str, message: str):
        self.log_event(f"warning:{warning_type}", {"message": message})

    def _prune_if_needed(self):
        cfg = self.config
        size_limit = 10 * 1024 * 1024
        if os.path.exists(self.log_path) and os.path.getsize(self.log_path) >= size_limit:
            self._rollover()
        elif self.entry_count >= cfg.get("max_entries", DEFAULT_CONFIG["max_entries"]):
            self._rollover()

        cutoff = datetime.now(timezone.utc) - timedelta(days=cfg.get("retain_days", DEFAULT_CONFIG["retain_days"]))
        for fname in os.listdir(self.log_dir):
            if not fname.endswith(".jsonl"):
                continue
            try:
                t = datetime.strptime(fname.replace(".jsonl", ""), "%Y%m%d_%H%M%S")
                if t.replace(tzinfo=timezone.utc) < cutoff:
                    os.remove(os.path.join(self.log_dir, fname))
            except Exception:
                continue

    def _rollover(self):
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.log_path = os.path.join(self.log_dir, f"{ts}.jsonl")
        self.entry_count = 0
