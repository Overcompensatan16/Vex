"""Unit tests for dorsal root conduction utilities."""

from __future__ import annotations

import importlib
import random
import sys
from pathlib import Path

import pytest


ROOT_DIR = str(Path(__file__).resolve().parents[2])
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import spinal_cord.dorsal_root as dorsal_root_module  # noqa: E402
import spinal_cord.scheduler as scheduler_module  # noqa: E402


class RecordingAuditLogger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, object]]] = []
        self.errors: list[tuple[str, str]] = []

    def log_event(self, event_type: str, data: dict) -> None:
        self.events.append((event_type, data))

    def log_error(self, error_type: str, message: str) -> None:
        self.errors.append((error_type, message))


@pytest.fixture
def fresh_modules():
    """Reload scheduler and dorsal root modules to reset global state."""

    scheduler = importlib.reload(scheduler_module)
    dorsal_root = importlib.reload(dorsal_root_module)
    return scheduler, dorsal_root


def test_symbolic_router_records_events_and_ordering(fresh_modules):
    scheduler, dorsal_root = fresh_modules

    thalamus = dorsal_root.ThalamusStub()
    brainstem = dorsal_root.BrainstemStub()
    audit_logger = RecordingAuditLogger()
    router = dorsal_root.SymbolicEventRouter(
        thalamus,
        brainstem,
        audit_logger=audit_logger,
    )

    distance_cm = 30.0
    weight = 0.5

    dorsal_root.afferent_fire("Aδ", distance_cm=distance_cm, weight=weight, target=router)
    dorsal_root.afferent_fire("C", distance_cm=distance_cm, weight=weight, target=router)

    scheduler.run_until(scheduler.now + 1000.0)

    thalamic_fibers = [event["fiber"] for event in thalamus.events]
    assert thalamic_fibers == ["Aδ", "C"]
    assert [event["fiber"] for event in brainstem.events] == thalamic_fibers
    assert all(event["weight"] == weight for event in thalamus.events)
    assert all(event["distance_cm"] == pytest.approx(distance_cm) for event in thalamus.events)
    assert all(event["source"] == dorsal_root.EVENT_SOURCE for event in thalamus.events)

    distance_m = distance_cm / 100.0
    expected_adelta_delay = (
            distance_m / dorsal_root.FIBER_VELOCITIES_M_PER_S["Aδ"] * 1000.0
    )
    expected_c_delay = distance_m / dorsal_root.FIBER_VELOCITIES_M_PER_S["C"] * 1000.0

    thalamic_times = [event["t"] for event in thalamus.events]
    assert thalamic_times[0] == pytest.approx(expected_adelta_delay)
    assert thalamic_times[1] == pytest.approx(expected_c_delay)
    assert [event["delay_ms"] for event in thalamus.events] == pytest.approx(
        [expected_adelta_delay, expected_c_delay]
    )

    assert [entry[0] for entry in audit_logger.events] == ["afferent_event", "afferent_event"]
    for (_, payload), expected_fiber in zip(audit_logger.events, thalamic_fibers):
        assert payload["fiber"] == expected_fiber
        assert payload["source"] == dorsal_root.EVENT_SOURCE
        assert payload["distance_cm"] == pytest.approx(distance_cm)
        assert payload["event"]["source"] == dorsal_root.EVENT_SOURCE
        assert payload["event"]["fiber"] == expected_fiber


def test_weight_function_shapes_intensity(fresh_modules):
    scheduler, dorsal_root = fresh_modules
    captured: list[tuple[float, float, str]] = []

    delays: list[float] = []

    def decay_weight(event_time: float, conduction_delay_ms: float, fiber: str) -> float:
        del fiber
        delays.append(conduction_delay_ms)
        return 1.0 / (1.0 + conduction_delay_ms / 10.0)

    def capture(event_time: float, weight: float, fiber: str) -> None:
        captured.append((event_time, weight, fiber))

    dorsal_root.afferent_fire(
        "Aβ",
        distance_cm=10.0,
        weight=decay_weight,
        target=capture,
    )

    scheduler.run_until(scheduler.now + 500.0)


def test_multiple_firings_queue_independent_events(fresh_modules):
    scheduler, dorsal_root = fresh_modules
    events: list[tuple[float, float, str]] = []

    def record(event_time: float, weight: float, fiber: str, **kwargs) -> None:
        events.append((event_time, weight, fiber))

    fibers = ["Aα", "Aβ", "Aδ", "C"]
    for index, fiber in enumerate(fibers, start=1):
        dorsal_root.afferent_fire(
            fiber,
            distance_cm=20.0,
            weight=float(index),
            target=record,
        )

    scheduler.run_until(scheduler.now + 1000.0)

    assert [fiber for _, _, fiber in events] == ["Aα", "Aβ", "Aδ", "C"]
    assert [weight for _, weight, _ in events] == [1.0, 2.0, 3.0, 4.0]


def test_symbolic_router_logs_consumer_errors(fresh_modules):
    scheduler, dorsal_root = fresh_modules

    class FailingConsumer:
        def receive(self, event):
            raise RuntimeError("boom")

    audit_logger = RecordingAuditLogger()
    failing = FailingConsumer()
    thalamus = dorsal_root.ThalamusStub()
    router = dorsal_root.SymbolicEventRouter(
        failing,
        thalamus,
        audit_logger=audit_logger,
    )

    dorsal_root.afferent_fire(
        "Aδ",
        distance_cm=10.0,
        weight=1.0,
        target=router,
    )

    scheduler.run_until(scheduler.now + 200.0)

    assert len(thalamus.events) == 1
    assert audit_logger.errors
    error_type, message = audit_logger.errors[0]
    assert error_type == "router_consumer_failure"
    assert "FailingConsumer" in message


def test_jitter_introduces_gaussian_variation(fresh_modules):
    scheduler, dorsal_root = fresh_modules
    events: list[tuple[float, float, str]] = []

    class RecordingRandom(random.Random):
        def __init__(self, seed: int) -> None:
            super().__init__(seed)
            self.samples: list[float] = []

        def gauss(self, mu, sigma, /):  # matches positional-only
            value = super().gauss(mu, sigma)
            self.samples.append(value)
            return value

    rng = RecordingRandom(42)

    dorsal_root.afferent_fire(
        "Aβ",
        distance_cm=10.0,
        weight=1.0,
        target=lambda *payload: events.append(payload),
        jitter_ms=2.0,
        rng=rng,
    )
