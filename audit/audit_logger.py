import json
from datetime import datetime, timezone
import os


class AuditLogger:
    def __init__(self, log_path="parietal_audit_log.jsonl"):
        self.log_path = log_path
        self._ensure_log_file_exists()
        print(f"[AuditLogger] Initialized. Logging to {self.log_path}")

    def _ensure_log_file_exists(self):
        # Ensure the directory for the log file exists
        log_dir = os.path.dirname(self.log_path)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
                print(f"[AuditLogger] Created log directory: {log_dir}")
            except OSError as e:
                print(f"[AuditLogger] Error creating log directory {log_dir}: {e}")

        # Create the log file if it doesn't exist
        try:
            with open(self.log_path, 'a') as f:
                pass  # Just open in append mode to create if not exists
        except IOError as e:
            print(f"[AuditLogger] Error ensuring log file exists at {self.log_path}: {e}")

    def log_event(self, event_type, data):
        """Logs a generic event to the audit log."""
        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = {
            "timestamp": timestamp,
            "type": event_type,
            "data": data
        }
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f)
                f.write('\n')  # Add newline for JSONL format
        except IOError as e:
            print(f"[AuditLogger] Error writing to audit log {self.log_path}: {e}")
        except Exception as e:
            print(f"[AuditLogger] Unexpected error logging event: {e}")

    def log_input(self, user_input):
        """Logs user input."""
        self.log_event("input", {"user_input": user_input})
        print(f"[AuditLogger] Logged user input: {user_input[:75]}{'...' if len(user_input) > 75 else ''}")

    def log_output(self, system_output):
        """Logs system output."""
        print_output = system_output
        if len(print_output) > 200:
            print_output = print_output[:197] + "..."

        self.log_event("output", {"system_output": system_output})
        print(f"[AuditLogger] Logged system output: {print_output}")

    def log_internal_state(self, module_name, state_data):
        """Logs a snapshot of an internal module's state."""
        self.log_event("internal_state", {"module": module_name, "state": state_data})

    def log_error(self, error_message, details=None):
        """Logs an error."""
        error_data = {"message": error_message, "details": details}
        self.log_event("error", error_data)

