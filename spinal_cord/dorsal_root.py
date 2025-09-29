# E:\Vex\spinal_cord\dorsal_root.py
"""Models dorsal root sensory fiber conduction delays."""

from __future__ import annotations

import logging
import random
from typing import Any, Callable, Dict, Optional, Sequence, Union

from audit.audit_logger_factory import AuditLoggerFactory
from spinal_cord import scheduler
from spinal_cord.audit_hooks import record_afferent_event, record_ascending_dispatch

logger = logging.getLogger(__name__)

EVENT_SOURCE = "dorsal_root"

EventTarget = Callable[..., None]
WeightFunction = Callable[[float, float, str], float]
WeightSpec = Union[float, WeightFunction]

# Approximate conduction velocities (m/s)
FIBER_VELOCITIES_M_PER_S: Dict[str, float] = {
    "Aα": 90.0,
    "Aβ": 50.0,
    "Aδ": 15.0,
    "C": 1.0,
    "Ia": 72.0,
    "Ib": 70.0,
    "II": 40.0,
}


def afferent_fire(
    fiber: str,
    *,
    distance_cm: float,
    weight: float,
    target: Callable[..., None],
    audit_logger: Optional[Any] = None,
    jitter_ms: Optional[float] = None,
    rng: Optional[random.Random] = None,
) -> None:
    """Schedule an afferent spike arrival.

    Why: simple callables may not accept kwargs; routers need rich context.
    - Jitter applies to scheduled time only.
    - Payload 'delay_ms' remains conduction-only for assertions.
    """
    if fiber not in FIBER_VELOCITIES_M_PER_S:
        raise KeyError(f"Unknown fiber type: {fiber}")

    distance_m = distance_cm / 100.0
    velocity = FIBER_VELOCITIES_M_PER_S[fiber]
    delay_ms = distance_m / velocity * 1000.0

    jitter = 0.0
    if jitter_ms is not None and jitter_ms > 0.0:
        rng = rng or random.Random()
        jitter = float(rng.gauss(0.0, float(jitter_ms)))

    effective_delay_ms = max(0.0, delay_ms + jitter)

    def _deliver(event_time: float) -> None:
        payload: dict[str, Any] = {
            "t": event_time,
            "fiber": fiber,
            "weight": weight,
            "delay_ms": delay_ms,
            "distance_cm": distance_cm,
            "source": EVENT_SOURCE,
        }

        # Avoid duplicate afferent audit when routed through SymbolicEventRouter
        from spinal_cord.dorsal_root import SymbolicEventRouter  # local import to avoid cycles
        is_router = isinstance(target, SymbolicEventRouter)
        if not is_router:
            record_afferent_event(audit_logger, payload)

        # Plain callable: positional-only to avoid kwarg TypeError with lambdas like lambda *args: ...
        if is_router:
            target(event_time, weight, fiber, delay_ms=delay_ms, distance_cm=distance_cm)
        else:
            target(event_time, weight, fiber)

    scheduled_time = scheduler.now + effective_delay_ms
    scheduler.schedule(scheduled_time, 0.0, _deliver)


class ThalamusStub:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def receive(self, event: dict[str, Any]) -> None:
        self.events.append(event)


class BrainstemStub:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def regulate(self, event: dict[str, Any]) -> None:
        self.events.append(event)


class SymbolicEventRouter:
    """Dispatch to consumers and record audit events."""

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
            consumer_list.append(self._log_event)  # one afferent_event per spike
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

    def _deliver_callable(
        self, consumer: Callable[[dict[str, Any]], None], event: dict[str, Any]
    ) -> None:
        try:
            consumer(event)
        except Exception as exc:
            self._log_consumer_error("callable", consumer, exc)
        else:
            record_ascending_dispatch(
                self._audit_logger,
                getattr(consumer, "__name__", consumer.__class__.__name__),
                event,
            )

    def _deliver_attr(self, consumer: Any, attr: str, event: dict[str, Any]) -> None:
        handler = getattr(consumer, attr, None)
        if not callable(handler):
            return
        try:
            handler(event)
        except Exception as exc:
            self._log_consumer_error(attr, consumer, exc)
        else:
            record_ascending_dispatch(
                self._audit_logger,
                f"{consumer.__class__.__name__}.{attr}",
                event,
            )

    def _log_event(self, event: dict[str, Any]) -> None:
        if self._audit_logger is not None:
            self._audit_logger.log_event(
                "afferent_event",
                {
                    "fiber": event["fiber"],
                    "source": EVENT_SOURCE,
                    "distance_cm": event.get("distance_cm"),
                    "event": event,
                },
            )

    def _log_consumer_error(self, entry_point: str, consumer: Any, exc: Exception) -> None:
        logger.exception(
            "SymbolicEventRouter consumer failure at %s for %r",
            entry_point,
            consumer,
            exc_info=exc,
        )
        if self._audit_logger is not None:
            try:
                self._audit_logger.log_error(
                    "router_consumer_failure",
                    f"{entry_point}:{consumer!r}:{exc}",
                )
            except Exception:
                logger.exception("Failed to audit consumer failure for %r", consumer)


def _dispatch_event(
    event_time: float,
    weight_spec: WeightSpec,
    fiber: str,
    target: EventTarget,
    conduction_delay_ms: float,
    distance_cm: float,
) -> None:
    """Internal helper (currently unused by router path)."""
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
                    "source": EVENT_SOURCE,
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
