from datetime import datetime, timezone

from audit.audit_logger import AuditLogger
from symbolic_signal import SymbolicSignal


class PrimaryAuditoryCortex:
    """Convert raw audio input into text facts."""

    def __init__(self, audit_log_path="cerebral_cortex/primary_auditory_cortex/auditory_audit_log.jsonl"):
        self.logger = AuditLogger(audit_log_path)
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
        except Exception as e:
            print(f"[PrimaryAuditoryCortex] Speech recognition unavailable: {e}")
            self.recognizer = None
        print("[PrimaryAuditoryCortex] Initialized.")

    def process(self, audio_input):
        """Return a ``SymbolicSignal`` from raw audio or text input."""
        transcript = ""
        if isinstance(audio_input, str):
            if self.recognizer and audio_input.lower().endswith((".wav", ".flac", ".aiff", ".mp3")):
                try:
                    import speech_recognition as sr
                    with sr.AudioFile(audio_input) as source:
                        audio = self.recognizer.record(source)
                        transcript = self.recognizer.recognize_google(audio)
                except Exception as e:
                    print(f"[PrimaryAuditoryCortex] STT failed: {e}")
                    transcript = audio_input
            else:
                transcript = audio_input
        else:
            transcript = str(audio_input)

        signal = SymbolicSignal(
            data={"text": transcript},
            modality="text",
            source="primary_auditory_cortex",
            tags=["audio"],
        )
        self.logger.log_event("auditory_output", signal.as_dict())
        return signal


__all__ = ["PrimaryAuditoryCortex"]
