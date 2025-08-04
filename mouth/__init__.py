from datetime import datetime, timezone

from audit.audit_logger import AuditLogger

try:
    import pyttsx3
    _engine = pyttsx3.init()
except Exception as e:
    _engine = None
    print(f"[MouthModule] pyttsx3 unavailable: {e}")


class MouthModule:
    """Simple TTS output handler."""

    def __init__(self, audit_log_path="mouth/mouth_audit_log.jsonl"):
        self.logger = AuditLogger(audit_log_path)
        self.engine = _engine
        print("[MouthModule] Initialized.")

    def speak(self, text: str):
        """Emit text via TTS or console."""
        event = {
            "text": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "mouth_module",
        }
        self.logger.log_event("speak", event)
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                event["status"] = "spoken"
            except Exception as e:
                print(f"[MouthModule] TTS error: {e}")
                event["status"] = "error"
        else:
            print(f"[MouthModule] {text}")
            event["status"] = "printed"
        return event


__all__ = ["MouthModule"]
