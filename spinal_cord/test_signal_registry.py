"""Tests for the signal registry reflex metadata integration."""

from __future__ import annotations

import pytest

from spinal_cord.signal_registry import REFLEX_REGISTRY, SignalRegistry


def test_reflex_registry_loaded() -> None:
    assert "spinal_cord.reflex.knee_jerk.receptor" in REFLEX_REGISTRY
    meta = REFLEX_REGISTRY["spinal_cord.reflex.knee_jerk.receptor"]
    assert meta["type"] == "analog"
    assert meta["units"] == "mV"


def test_registry_autoregisters_reflex_paths() -> None:
    registry = SignalRegistry()
    meta = registry.metadata("system.anesthesia.engaged")
    assert meta["type"] == "digital"
    assert registry.get("system.anesthesia.engaged") is False


@pytest.mark.parametrize(
    "path, value, expected",
    [
        ("autonomic.reflex.baroreceptor", 120, 120.0),
        ("autonomic.reflex.breathing.rhythm", 0.3, 0.3),
    ],
)
def test_analog_and_oscillatory_values_are_coerced_to_float(path: str, value: float, expected: float) -> None:
    registry = SignalRegistry()
    stored = registry.set(0.0, path, value)
    assert stored == pytest.approx(expected)
    assert isinstance(registry.get(path), float)


def test_analog_type_rejects_non_numeric() -> None:
    registry = SignalRegistry()
    with pytest.raises(TypeError):
        registry.set(0.0, "autonomic.reflex.baroreceptor", "high")


def test_digital_type_rejects_numeric_values() -> None:
    registry = SignalRegistry()
    with pytest.raises(TypeError):
        registry.set(0.0, "system.anesthesia.engaged", 1)
