from __future__ import annotations

import importlib
from typing import Any, Dict, List, Tuple

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest

from spinal_cord.reflex_coordinator import ReflexArc, ReflexOrchestrator
from spinal_cord.reflex_types import DorsalHornReflex, ProprioEvent, ReflexContext
from spinal_cord.signal_registry import SignalRegistry


@pytest.fixture(autouse=True)
def reset_scheduler() -> None:
    import spinal_cord.scheduler as sched

    importlib.reload(sched)
    yield


@pytest.fixture
def registry() -> SignalRegistry:
    reg = SignalRegistry()

    assert reg.get("system.analgesia.level") == pytest.approx(0.0)
    assert reg.get("system.anesthesia.engaged") is False
    assert reg.get("system.cooldown.active") is False

    required_paths = (
        "right_arm.biceps.contraction",
        "right_arm.triceps.inhibition",
        "left_arm.triceps.activation",
        "left_arm.biceps.inhibition",
        "right_leg.flexor.contraction",
        "left_leg.flexor.contraction",
    )
    for path in required_paths:
        reg.metadata(path)

    return reg


@pytest.fixture
def motor_bus() -> "FakeMotorBus":
    return FakeMotorBus()


@pytest.fixture
def orchestrator(registry: SignalRegistry, motor_bus: "FakeMotorBus") -> ReflexOrchestrator:
    region_map = {
        "right_arm": {
            "flexor": "biceps",
            "extensor": "triceps",
            "joint": "elbow",
            "crossed_extensor": {
                "region": "left_arm",
                "extensor": "triceps",
                "flexor": "biceps",
                "joint": "elbow",
            },
        },
        "left_arm": {
            "flexor": "biceps",
            "extensor": "triceps",
            "joint": "elbow",
        },
    }
    return ReflexOrchestrator(motor_bus=motor_bus, registry=registry, region_map=region_map)


class FakeMotorBus:
    def __init__(self) -> None:
        self.events: List[Dict[str, Any]] = []

    def drive_on(self, time_ms: float, region: str, muscle: str, level: float, intent: str) -> None:
        self.events.append(
            {
                "phase": "on",
                "time": time_ms,
                "region": region,
                "muscle": muscle,
                "level": level,
                "intent": intent,
            }
        )

    def drive_off(self, time_ms: float, region: str, muscle: str, intent: str) -> None:
        self.events.append(
            {
                "phase": "off",
                "time": time_ms,
                "region": region,
                "muscle": muscle,
                "intent": intent,
            }
        )


def test_reflex_arc_dispatch(registry: SignalRegistry) -> None:
    ctx = ReflexContext(
        event=DorsalHornReflex(t=0.0, region="right_arm", label="withdrawal", fiber="Aδ", weight=0.9),
        region="right_arm",
        registry=registry,
        region_state={},
        region_config={"flexor": "biceps", "extensor": "triceps", "joint": "elbow"},
    )

    arc = ReflexArc("withdrawal", ctx)
    rule = arc.build_rules()[0]
    assert rule.name == "flexor_withdrawal"

    crossed = ReflexArc("crossed_extensor", ctx).build_rules()[0]
    assert crossed.name == "crossed_extensor"


def test_withdrawal_reflex_schedules_drives_and_signals(
    orchestrator: ReflexOrchestrator,
    registry: SignalRegistry,
    motor_bus: FakeMotorBus,
) -> None:
    updates: List[Tuple[Any, ...]] = []
    contralateral_updates: List[Tuple[Any, ...]] = []
    registry.subscribe("right_arm", lambda *args: updates.append(args))
    registry.subscribe("left_arm", lambda *args: contralateral_updates.append(args))

    event = DorsalHornReflex(t=0.0, region="right_arm", label="withdrawal", fiber="Aδ", weight=0.9)
    winners = orchestrator.receive(event)
    assert {rule.name for rule in winners} >= {"flexor_withdrawal", "crossed_extensor"}

    import spinal_cord.scheduler as sched

    sched.run_until(25.0)
    assert motor_bus.events[0]["phase"] == "on"
    assert motor_bus.events[0]["time"] == pytest.approx(20.0)
    assert motor_bus.events[0]["region"] == "right_arm"
    assert motor_bus.events[0]["muscle"] == "biceps"

    sched.run_until(200.0)
    assert any(ev["phase"] == "off" and ev["time"] == pytest.approx(140.0) for ev in motor_bus.events)

    on_updates = [u for u in updates if u[1] > 0.0]
    off_updates = [u for u in updates if abs(u[1]) < 1e-6]
    assert any(path.endswith("biceps.contraction") for path, _, _, _, _ in on_updates)
    assert all(abs(value) < 1e-6 for _, value, _, _, _ in off_updates)

    contra_on = [u for u in contralateral_updates if u[1] > 0.0]
    assert any(path == "left_arm.triceps.activation" for path, _, _, _, _ in contra_on)
    assert any(path == "left_arm.elbow.extension_intent" for path, _, _, _, _ in contralateral_updates)


def test_monosynaptic_stretch_fires_before_withdrawal(
    orchestrator: ReflexOrchestrator,
    registry: SignalRegistry,
    motor_bus: FakeMotorBus,
) -> None:
    stretch_event = ProprioEvent(
        t=0.0,
        region="right_arm",
        kind="Ia",
        muscle="biceps",
        antagonist="triceps",
        magnitude=0.8,
    )
    withdrawal_event = DorsalHornReflex(
        t=0.0,
        region="right_arm",
        label="withdrawal",
        fiber="Aδ",
        weight=0.9,
    )

    orchestrator.receive(stretch_event)
    orchestrator.receive(withdrawal_event)

    import spinal_cord.scheduler as sched

    sched.run_until(30.0)
    on_events = [event for event in motor_bus.events if event["phase"] == "on"]
    assert on_events[0]["time"] == pytest.approx(6.0)
    assert on_events[0]["muscle"] == "biceps"
    assert any(
        ev["time"] == pytest.approx(20.0)
        for ev in on_events
        if ev["region"] == "right_arm" and ev["muscle"] == "biceps"
    )


def test_analgesia_blocks_low_weight_withdrawal(
    orchestrator: ReflexOrchestrator,
    registry: SignalRegistry,
    motor_bus: FakeMotorBus,
) -> None:
    registry.set("system.analgesia.level", 0.8)
    event = DorsalHornReflex(t=5.0, region="right_arm", label="withdrawal", fiber="Aδ", weight=0.2)
    orchestrator.receive(event)

    import spinal_cord.scheduler as sched

    sched.run_until(200.0)
    assert all(ev.get("intent") != "flexor_withdrawal" for ev in motor_bus.events)


def test_cooldown_blocks_lower_priority(
    orchestrator: ReflexOrchestrator,
    registry: SignalRegistry,
    motor_bus: FakeMotorBus,
) -> None:
    first = DorsalHornReflex(t=0.0, region="right_arm", label="withdrawal", fiber="Aδ", weight=0.9)
    orchestrator.receive(first)

    import spinal_cord.scheduler as sched

    second = ProprioEvent(
        t=10.0,
        region="right_arm",
        kind="Ia",
        muscle="biceps",
        antagonist="triceps",
        magnitude=0.9,
    )
    orchestrator.receive(second)

    sched.run_until(200.0)
    stretch_events = [event for event in motor_bus.events if event.get("intent") == "monosynaptic_stretch"]
    assert not stretch_events


def test_signal_clamping_and_versioning() -> None:
    registry = SignalRegistry()
    registry.register("right_arm.test.signal", {"range": (0.0, 1.0), "baseline": 0.0})
    updates: List[Tuple[Any, ...]] = []
    registry.subscribe("right_arm", lambda *args: updates.append(args))

    registry.set("right_arm.test.signal", 2.5)
    assert registry.get("right_arm.test.signal") == pytest.approx(1.0)
    assert registry.version("right_arm.test.signal") == 1

    registry.set("right_arm.test.signal", -1.0)
    assert registry.get("right_arm.test.signal") == pytest.approx(0.0)
    assert registry.version("right_arm.test.signal") == 2

    assert updates[0][1] == pytest.approx(1.0)
    assert updates[0][2] == 1
    assert updates[1][1] == pytest.approx(0.0)
    assert updates[1][2] == 2


def test_anesthesia_gates_reflexes(
    orchestrator: ReflexOrchestrator,
    registry: SignalRegistry,
    motor_bus: FakeMotorBus,
) -> None:
    registry.set("system.anesthesia.engaged", True)
    event = DorsalHornReflex(t=0.0, region="right_arm", label="withdrawal", fiber="Aδ", weight=0.9)
    orchestrator.receive(event)

    import spinal_cord.scheduler as sched

    sched.run_until(200.0)
    assert not motor_bus.events
    assert registry.get("system.anesthesia.engaged") is True