"""Utility helpers for emitting spinal cord audit events."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Optional

__all__ = [
    "record_afferent_event",
    "record_dorsal_summary",
    "record_motor_command",
    "record_motor_drive",
    "record_signal_event",
    "record_ascending_dispatch",
]


def _safe_log(audit_logger: Any, event_type: str, payload: Mapping[str, Any]) -> None:
    """Safely proxy *payload* to ``audit_logger.log_event`` if available."""

    if audit_logger is None:
        return

    log_event = getattr(audit_logger, "log_event", None)
    if not callable(log_event):
        return

    try:
        log_event(event_type, dict(payload))
    except Exception:  # pragma: no cover - audit logging is best-effort only
        pass


def _coerce_event_mapping(event: Any) -> MutableMapping[str, Any]:
    if isinstance(event, MutableMapping):
        return dict(event)
    if isinstance(event, Mapping):
        return dict(event)
    return {"value": event}


def record_afferent_event(audit_logger: Any, event: Any) -> None:
    """Log an afferent arrival originating from the dorsal root."""

    event_map = _coerce_event_mapping(event)
    payload = {"stage": "dorsal_root", "event": event_map}
    if "t" in event_map:
        payload["t"] = event_map["t"]
    elif "time_ms" in event_map:
        payload["t"] = event_map["time_ms"]
    payload.setdefault("fiber", event_map.get("fiber"))
    payload.setdefault("delay_ms", event_map.get("delay_ms"))
    payload.setdefault("distance_cm", event_map.get("distance_cm"))
    payload.setdefault("source", event_map.get("source"))
    _safe_log(audit_logger, "spinal_afferent", payload)


def record_dorsal_summary(audit_logger: Any, summary: Mapping[str, Any]) -> None:
    """Log the outcome of dorsal horn processing."""

    if summary is None:
        return
    payload = {
        "stage": "dorsal_horn",
        "overall": summary.get("overall"),
        "reflexes": summary.get("reflexes"),
        "stimulus": summary.get("stimulus"),
        "modulation": summary.get("modulation"),
    }
    _safe_log(audit_logger, "spinal_dorsal_summary", payload)


def record_motor_command(audit_logger: Any, command: Any) -> None:
    """Log a motor command emitted by the ventral horn."""

    if command is None:
        return

    payload = {
        "stage": "ventral_horn",
        "t": getattr(command, "t", None),
        "muscle": getattr(command, "muscle", None),
        "activation": getattr(command, "activation", None),
        "region": getattr(command, "region", None),
        "signals": getattr(command, "signals", None),
        "twitch_events": getattr(command, "twitch_events", None),
    }
    _safe_log(audit_logger, "spinal_motor_command", payload)


def record_motor_drive(
    audit_logger: Any,
    *,
    phase: str,
    time_ms: float,
    region: str,
    muscle: str,
    intent: str,
    level: Optional[float] = None,
) -> None:
    """Log scheduler-triggered changes to motor drive levels."""

    payload = {
        "stage": "ventral_horn",
        "phase": phase,
        "t": time_ms,
        "region": region,
        "muscle": muscle,
        "intent": intent,
    }
    if level is not None:
        payload["level"] = level
    _safe_log(audit_logger, "spinal_motor_drive", payload)


def record_signal_event(
    audit_logger: Any,
    *,
    phase: str,
    time_ms: float,
    path: str,
    value: Any,
    rule: Optional[str] = None,
) -> None:
    """Log scheduler-driven updates to symbolic signals."""

    payload = {
        "stage": "signal_registry",
        "phase": phase,
        "t": time_ms,
        "path": path,
        "value": value,
    }
    if rule is not None:
        payload["rule"] = rule
    _safe_log(audit_logger, "spinal_signal", payload)


def record_ascending_dispatch(audit_logger: Any, target: str, event: Mapping[str, Any]) -> None:
    """Log propagation of afferent data to ascending targets."""

    payload = {
        "stage": "ascending_pathway",
        "target": target,
        "event": dict(event),
    }
    if "t" in event:
        payload["t"] = event["t"]
    _safe_log(audit_logger, "spinal_ascending", payload)