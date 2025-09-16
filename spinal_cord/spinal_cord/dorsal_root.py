"""Models dorsal root sensory fiber conduction delays."""

from __future__ import annotations

import logging
import random
from typing import Any, Callable, Dict, Optional, Sequence, Union

from audit.audit_logger_factory import AuditLoggerFactory

from . import scheduler

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
    if callable(weight_spec):
        shaped_weight = float(weight_spec(event_time, conduction_delay_ms, fiber))
        return any(f"unexpected keyword argument '{key}'" in message for key in keywords)

        def afferent_fire(
                fiber: str,
                distance_cm: float,
                weight: WeightSpec,
                target: EventTarget,
                *,
                jitter_ms: float = 0.0,
                rng: Optional[random.Random] = None,
        ) -> int:
            """Schedule a dorsal horn target to fire once the afferent reaches it.

            The function converts anatomical distance and fiber class into a synaptic
            delay and delegates to :mod:`spinal_cord.scheduler` to deliver the
            resulting event.  Optional ``jitter_ms`` introduces Gaussian noise to the
            arrival time, and ``weight`` may be a callable that derives the delivered
            intensity based on the final timing or fiber class.

            Args:
                fiber: A key from :data:`FIBER_VELOCITIES_M_PER_S` identifying the
                    afferent class (e.g. ``"Aδ"`` or ``"C"``).
                distance_cm: Path length in centimetres from receptor to dorsal horn.
                weight: Either a scalar intensity or a callable returning the intensity
                    given ``(event_time, conduction_delay_ms, fiber)``.  Callables can
                    model synaptic fatigue, e.g. ``lambda _, delay_ms, __: base_weight *
                    math.exp(-delay_ms / 50.0)`` (after ``import math``) to reduce the
                    delivered weight as the conduction delay grows.
                target: Callable invoked as ``target(event_time, weight, fiber)`` when
                    the signal arrives.  Targets may optionally accept the keyword
                    arguments ``delay_ms`` and ``distance_cm`` for richer context.
                jitter_ms: Standard deviation of Gaussian noise applied to the
                    conduction delay.  Defaults to ``0`` for deterministic behaviour.
                rng: Optional random-number generator supplying the jitter samples.  The
                    global :mod:`random` generator is used when omitted.

            Returns:
                Scheduler event identifier for the queued synaptic activation.

            Raises:
                ValueError: If the fiber type is unknown or if ``distance_cm`` or
                    ``jitter_ms`` are invalid.
            """

            if fiber not in FIBER_VELOCITIES_M_PER_S:
                raise ValueError(f"Unknown afferent fiber type: {fiber!r}")

            if distance_cm < 0:
                raise ValueError("distance_cm must be non-negative")

            if jitter_ms < 0:
                raise ValueError("jitter_ms must be non-negative")
                # Convert centimetres to metres then to a millisecond delay.
                distance_m = distance_cm / 100.0
                base_delay_ms = (distance_m / velocity) * 1000.0

                actual_delay_ms = base_delay_ms
                if jitter_ms:
                    generator = rng if rng is not None else random
                    noise = generator.gauss(0.0, float(jitter_ms))
                    actual_delay_ms = max(0.0, base_delay_ms + noise)

                scheduled_time = scheduler.now + actual_delay_ms
                return scheduler.schedule(
                    scheduled_time,
                    0.0,
                    _dispatch_event,
                    weight,
                    fiber,
                    target,
                    actual_delay_ms,
                    distance_cm,
                )

            __all__ = [
                "FIBER_VELOCITIES_M_PER_S",
                "EVENT_SOURCE",
                "SymbolicEventRouter",
                "ThalamusStub",
                "BrainstemStub",
                "afferent_fire",
            ]
