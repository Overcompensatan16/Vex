from datetime import datetime, timezone
from typing import Optional

from symbolic_signal import SymbolicSignal
from audit.audit_logger_factory import AuditLoggerFactory
from cerebral_cortex.temporal_lobe.context_tracker import ContextTracker


class PrimaryAuditoryCortex:
    """Convert raw transcripts into SymbolicSignal objects."""

    def __init__(self, audit_log_path=None, context_size: int = 10):
        self.logger = AuditLoggerFactory("primary_auditory_cortex", log_path=audit_log_path)
        self.context = ContextTracker(max_size=context_size)

    def process(self, transcript: Optional[str]) -> SymbolicSignal:
        """Return a SymbolicSignal from a text transcript."""
        text = transcript or ""
        self.logger.log_event("transcript_in", {"text": text})
        signal = SymbolicSignal(
            data={"text": text},
            modality="audio",
            source="primary_auditory_cortex",
        )
        signal.timestamp = datetime.now(timezone.utc).isoformat()
        self.logger.log_event("signal_out", signal.as_dict())
        self.context.add(signal.as_dict())
        return signal


__all__ = ["PrimaryAuditoryCortex"]
