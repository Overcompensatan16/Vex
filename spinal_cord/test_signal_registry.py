"""Tests for the reflex signal indexer and runtime registry integration."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest


def _load_signal_registry_module():
    module_path = Path(__file__).with_name("signal_registry.py")
    package_name = "spinal_cord"
    if package_name not in sys.modules:
        package = types.ModuleType(package_name)
        package.__path__ = [str(module_path.parent)]  # type: ignore[attr-defined]
        sys.modules[package_name] = package
    spec = importlib.util.spec_from_file_location("spinal_cord.signal_registry", module_path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError("Unable to load spinal_cord.signal_registry module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


_signal_registry = _load_signal_registry_module()
SignalRegistry = _signal_registry.SignalRegistry
REFLEX_REGISTRY = _signal_registry.REFLEX_REGISTRY
REFLEX_INDEX = _signal_registry.REFLEX_INDEX


def test_indexer_groups_reflexes_by_subsystem() -> None:
    arcs = REFLEX_INDEX.get_by_subsystem("autonomic_cardiac")
    names = {arc.name for arc in arcs}
    assert {"baroreceptor", "bainbridge", "diving"}.issubset(names)


def test_indexer_field_lookup_merges_sources() -> None:
    vagal_matches = {arc.name for arc in REFLEX_INDEX.get_by_afferent("vagal visceral afferents")}
    assert "vomiting" in vagal_matches

    protective = {arc.name for arc in REFLEX_INDEX.get_by_response_type("protective")}
    assert {"vomiting", "blink"}.issubset(protective)


def test_registry_autoregisters_system_signals() -> None:
    assert "system.anesthesia" in REFLEX_REGISTRY
    registry = SignalRegistry()
    meta = registry.metadata("system.anesthesia")
    assert meta["type"] == "digital"
    assert registry.get("system.anesthesia") is False


@pytest.mark.parametrize(
    "path, value, expected",
    [
        ("system.baroreflex_setpoint", 120, 120.0),
        ("system.respiratory_rhythm", 0.3, 0.3),
    ],
)
def test_numeric_signals_are_coerced_to_float(path: str, value: float, expected: float) -> None:
    registry = SignalRegistry()
    stored = registry.set(path, value)
    assert stored == pytest.approx(expected)
    assert isinstance(registry.get(path), float)


def test_analog_type_rejects_non_numeric() -> None:
    registry = SignalRegistry()
    with pytest.raises(TypeError):
        registry.set("system.baroreflex_setpoint", "high")


def test_digital_type_rejects_numeric_values() -> None:
    registry = SignalRegistry()
    with pytest.raises(TypeError):
        registry.set("system.anesthesia", 1)