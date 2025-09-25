import pytest
from typing import Any, List, Tuple
import json
from pathlib import Path

from spinal_cord.reflex_coordinator import ReflexOrchestrator
from spinal_cord.signal_registry import SignalRegistry
from spinal_cord.reflex_types import DorsalHornReflex, ProprioEvent

# ---------------------------------------------------------------------
# Load external reflex signal map once for all tests
# ---------------------------------------------------------------------

SIGNAL_MAP_PATH = Path(r"E:\VexSignalRegistry\reflex_signals\reflex_signal_map.json")


def preload_signals(registry: SignalRegistry) -> None:
    """Register all signals from reflex_signals.json into the registry."""
    with open(SIGNAL_MAP_PATH, "r") as f:
        signal_map = json.load(f)

    for path, cfg in signal_map.items():
        # Ensure defaults exist
        if "range" not in cfg:
            cfg["range"] = (0.0, 1.0)
        if "baseline" not in cfg:
            cfg["baseline"] = 0.0
        registry.register(path, cfg)


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def registry() -> SignalRegistry:
    reg = SignalRegistry()
    preload_signals(reg)
    return reg


class FakeMotorBus:
    """Test double for motor bus used by reflex coordinator."""

    def __init__(self) -> None:
        self.events: List[dict[str, Any]] = []

    def drive(self, time: float, region: str, muscle: str, phase: str) -> None:
        self.events.append(
            {"time": time, "region": region, "muscle": muscle, "phase": phase}
        )


@pytest.fixture
def motor_bus() -> FakeMotorBus:
    return FakeMotorBus()


@pytest.fixture
def orchestrator(registry: SignalRegistry, motor_bus: FakeMotorBus) -> ReflexOrchestrator:
    return ReflexOrchestrator(registry=registry, motor_bus=motor_bus)


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------

def test_reflex_arc_dispatch(orchestrator: ReflexOrchestrator, registry: SignalRegistry) -> None:
    event = DorsalHornReflex(
        t=0.0, region="right_leg", label="withdrawal", fiber="Aδ", weight=1.0
    )
    winners = orchestrator.receive(event)
    assert any(rule.name == "flexor_withdrawal" for rule in winners)


def test_withdrawal_reflex_schedules_drives_and_signals(
    orchestrator: ReflexOrchestrator,
    registry: SignalRegistry,
    motor_bus: FakeMotorBus,
) -> None:
    updates: List[Tuple[Any, ...]] = []
    registry.subscribe("right_arm", lambda *args: updates.append(args))

    event = DorsalHornReflex(
        t=0.0, region="right_arm", label="withdrawal", fiber="Aδ", weight=0.9
    )
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

    # Ensure contraction signals were raised
    assert any(
        isinstance(path, str) and path.endswith("contraction") and value > 0.0
        for _, path, value, *_ in updates
    )


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
        t=0.0, region="right_arm", label="withdrawal", fiber="Aδ", weight=0.9
    )

    orchestrator.receive(stretch_event)
    winners = orchestrator.receive(withdrawal_event)

    assert any(rule.name == "stretch_reflex" for rule in winners)


def test_analgesia_blocks_low_weight_withdrawal(
    orchestrator: ReflexOrchestrator,
    registry: SignalRegistry,
    motor_bus: FakeMotorBus,
) -> None:
    registry.set("system.analgesia.level", 0.8)
    event = DorsalHornReflex(
        t=0.0, region="right_arm", label="withdrawal", fiber="Aδ", weight=0.2
    )
    winners = orchestrator.receive(event)
    assert winners == []


def test_cooldown_blocks_lower_priority(
    orchestrator: ReflexOrchestrator,
    registry: SignalRegistry,
    motor_bus: FakeMotorBus,
) -> None:
    first = DorsalHornReflex(
        t=0.0, region="right_arm", label="withdrawal", fiber="Aδ", weight=0.9
    )
    second = DorsalHornReflex(
        t=5.0, region="right_arm", label="withdrawal", fiber="Aδ", weight=0.2
    )

    winners1 = orchestrator.receive(first)
    winners2 = orchestrator.receive(second)

    assert any(rule.name == "flexor_withdrawal" for rule in winners1)
    assert winners2 == []


def test_signal_clamping_and_versioning() -> None:
    registry = SignalRegistry()
    preload_signals(registry)

    registry.register("right_arm.test.signal", {"range": (0.0, 1.0), "baseline": 0.0})
    updates: List[Tuple[Any, ...]] = []
    registry.subscribe("right_arm", lambda *args: updates.append(args))

    registry.set("right_arm.test.signal", 2.5)
    assert registry.get("right_arm.test.signal") == pytest.approx(1.0)
    assert registry.version("right_arm.test.signal") == 1
    assert updates[0][2] in (2.5, 1.0)

    registry.set("right_arm.test.signal", -1.0)
    assert registry.get("right_arm.test.signal") == pytest.approx(0.0)
    assert registry.version("right_arm.test.signal") == 2
    assert updates[1][2] in (-1.0, 0.0)


def test_anesthesia_gates_reflexes(
    orchestrator: ReflexOrchestrator,
    registry: SignalRegistry,
    motor_bus: FakeMotorBus,
) -> None:
    registry.set("system.anesthesia.engaged", True)
    event = DorsalHornReflex(
        t=0.0, region="right_arm", label="withdrawal", fiber="Aδ", weight=0.9
    )
    winners = orchestrator.receive(event)
    assert winners == []
