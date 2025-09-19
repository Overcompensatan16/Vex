"""Models dorsal root sensory fiber conduction delays."""

from __future__ import annotations

import logging
import random
from typing import Any, Callable, Dict, Optional, Sequence, Union

from audit.audit_logger_factory import AuditLoggerFactory

from spinal_cord import scheduler

logger = logging.getLogger(__name__)

EVENT_SOURCE = "dorsal_root"

EventTarget = Callable[..., None]
WeightFunction = Callable[[float, float, str], float]
WeightSpec = Union[float, WeightFunction]

# Approximate conduction velocities for common afferent fiber classes in meters
# per second.  Values are representative rather than exhaustive and are sourced
# from typical neurophysiology ranges.  Only a subset is presently used by the
# simulation but the dictionary provides room for expansion.
FIBER_VELOCITIES_M_PER_S: Dict[str, float] = {
    "Aα": 90.0,
    "Aβ": 50.0,
    "Aδ": 15.0,
    "C": 1.0,
    # Muscle spindle / Golgi tendon organ classes retained for compatibility.
    "Ia": 72.0,
    "Ib": 70.0,
    "II": 40.0,
}


def afferent_fire(
    fiber: str,
    distance_cm: float,
    weight: Union[float, Callable[[float, float, str], float]],
    target: Union[Callable[[float, float, str], None], object],
    jitter_ms: float = 0.0,
    rng: Optional[random.Random] = None,
    audit_logger: Optional[object] = None,
) -> None:
    """
    Fire an afferent sensory signal into the dorsal root.

    Args:
        fiber: Fiber type ("Aα", "Aβ", "Aδ", "C").
        distance_cm: Conduction distance in centimeters.
        weight: Either a float or a callable(weight_fn(event_time, delay_ms, fiber)).
        target: Consumer (callable or object with .receive()).
        jitter_ms: Gaussian jitter (stddev in ms).
        rng: Optional random.Random for reproducibility.
        audit_logger: Optional logger with .log_event / .log_error methods.
    """
    if fiber not in FIBER_VELOCITIES_M_PER_S:
        raise ValueError(f"Unknown fiber type: {fiber}")

    velocity_m_per_s = FIBER_VELOCITIES_M_PER_S[fiber]
    distance_m = distance_cm / 100.0
    conduction_delay_s = distance_m / velocity_m_per_s
    conduction_delay_ms = conduction_delay_s * 1000.0

    # Apply jitter
    if jitter_ms > 0.0:
        rng = rng or random
        conduction_delay_ms += rng.gauss(0.0, jitter_ms)

    scheduled_time = scheduler.now + conduction_delay_ms

    # inside afferent_fire
    def _deliver(event_time: float) -> None:
        """Deliver payload to target when scheduler fires."""
        if callable(weight):
            try:
                actual_weight = weight(event_time, conduction_delay_ms, fiber)
            except Exception as exc:
                if audit_logger and hasattr(audit_logger, "log_error"):
                    audit_logger.log_error("weight_function_failure", str(exc))
                return
        else:
            actual_weight = float(weight)

        payload = {
            "time_ms": event_time,
            "fiber": fiber,
            "weight": actual_weight,
            "delay_ms": conduction_delay_ms,
            "distance_cm": distance_cm,
            "source": EVENT_SOURCE,
        }

        try:
            if hasattr(target, "receive"):
                target.receive(payload)
            else:
                target(event_time, actual_weight, fiber,
                       delay_ms=conduction_delay_ms,
                       distance_cm=distance_cm)
        except Exception as exc:
            if audit_logger and hasattr(audit_logger, "log_error"):
                audit_logger.log_error(
                    "router_consumer_failure",
                    f"{type(target).__name__} failed: {exc}"
                )
            return  # don't re-raise, let other consumers work

        if audit_logger and hasattr(audit_logger, "log_event"):
            audit_logger.log_event("afferent_event", payload)

    # schedule call remains
    scheduler.schedule(scheduled_time, 0.0, _deliver)


class ThalamusStub:
    """Minimal stub that records events routed through ``receive``."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def receive(self, event: dict[str, Any]) -> None:
        self.events.append(event)


class BrainstemStub:
    """Minimal stub that records events routed through ``regulate``."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def regulate(self, event: dict[str, Any]) -> None:
        self.events.append(event)


class SymbolicEventRouter:
    """Dispatch afferent arrivals to a collection of integration stubs.

    The router mirrors the informal ``record_event`` helper mentioned in the
    design discussion by packaging the simulation payload into a dictionary and
    forwarding it to any supplied stubs.  Consumers may expose ``receive`` and
    ``regulate`` methods or be simple callables that accept the event mapping
    directly.  Event dictionaries include ``source="dorsal_root"`` along with
    ``delay_ms`` and ``distance_cm`` when the firing code supplies that
    metadata.  The router can automatically log each event via
    :class:`~audit.audit_logger_factory.AuditLoggerFactory` and
    will isolate failing consumers so the broader routing pipeline continues to
    operate.  The router itself is callable and therefore compatible with
    :func:`afferent_fire`'s ``target`` argument.
    """

    def __init__(
        self,
        *consumers: Any,
        audit_logger: Optional[AuditLoggerFactory] = None,
        enable_audit_logging: bool = True,
    ) -> None:
        if audit_logger is None and enable_audit_logging:
            audit_logger = AuditLoggerFactory("dorsal_root")

        self._audit_logger = audit_logger
        consumer_list: list[Any] = []
        if self._audit_logger is not None:
            consumer_list.append(self._log_event)
        consumer_list.extend(consumers)
        self._consumers: Sequence[Any] = tuple(consumer_list)

    def __call__(
        self,
        event_time: float,
        weight: float,
        fiber: str,
        *,
        delay_ms: Optional[float] = None,
        distance_cm: Optional[float] = None,
    ) -> None:
        event: dict[str, Any] = {
            "t": event_time,
            "weight": weight,
            "fiber": fiber,
            "source": EVENT_SOURCE,
        }
        if delay_ms is not None:
            event["delay_ms"] = delay_ms
        if distance_cm is not None:
            event["distance_cm"] = distance_cm

        for consumer in self._consumers:
            if callable(consumer):
                self._deliver_callable(consumer, event)
                continue

            self._deliver_attr(consumer, "receive", event)
            self._deliver_attr(consumer, "regulate", event)

    def _deliver_callable(self, consumer: Callable[[dict[str, Any]], None], event: dict[str, Any]) -> None:
        try:
            consumer(event)
        except Exception as exc:  # pragma: no cover - defensive fallback
            self._log_consumer_error("callable", consumer, exc)

    def _deliver_attr(self, consumer: Any, attr: str, event: dict[str, Any]) -> None:
        handler = getattr(consumer, attr, None)
        if not callable(handler):
            return
        try:
            handler(event)
        except Exception as exc:
            self._log_consumer_error(attr, consumer, exc)

    def _log_event(self, event: dict[str, Any]) -> None:
        if self._audit_logger is None:
            return
        try:
            payload = {
                "event": dict(event),
                "fiber": event.get("fiber"),
                "distance_cm": event.get("distance_cm"),
                "source": event.get("source", EVENT_SOURCE),
            }
            self._audit_logger.log_event("afferent_event", payload)
        except Exception:  # pragma: no cover - audit logging should rarely fail
            logger.exception("Failed to audit dorsal root event")

    def _log_consumer_error(self, entry_point: str, consumer: Any, exc: Exception) -> None:
        logger.exception("SymbolicEventRouter consumer failure at %s for %r", entry_point, consumer, exc_info=exc)
        if self._audit_logger is not None:
            try:
                self._audit_logger.log_error(
                    "router_consumer_failure",
                    f"{entry_point}:{consumer!r}:{exc}",
                )
            except Exception:  # pragma: no cover - defensive logging
                logger.exception("Failed to audit consumer failure for %r", consumer)


def _dispatch_event(
    event_time: float,
    weight_spec: WeightSpec,
    fiber: str,
    target: EventTarget,
    conduction_delay_ms: float,
    distance_cm: float,
) -> None:
    """Internal helper to deliver an event to the target."""
    if callable(weight_spec):
        try:
            shaped_weight = float(weight_spec(event_time, conduction_delay_ms, fiber))
        except Exception as exc:
            logging.exception("Weight function failed for %s", fiber, exc_info=exc)
            return
    else:
        shaped_weight = float(weight_spec)

    try:
        if hasattr(target, "receive"):
            target.receive(
                {
                    "time_ms": event_time,
                    "fiber": fiber,
                    "weight": shaped_weight,
                    "delay_ms": conduction_delay_ms,
                    "distance_cm": distance_cm,
                    "source": "dorsal_root",
                }
            )
        else:
            target(event_time, shaped_weight, fiber)
    except Exception as exc:
        logging.exception("Dispatch target failed for %s", fiber, exc_info=exc)


__all__ = [
    "FIBER_VELOCITIES_M_PER_S",
    "EVENT_SOURCE",
    "SymbolicEventRouter",
    "ThalamusStub",
    "BrainstemStub",
    "afferent_fire",
]
