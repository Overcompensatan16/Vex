"""Core spinal cord abstractions."""

from __future__ import annotations

from importlib import import_module
from typing import Any, Dict, Iterable, TYPE_CHECKING

try:  # pragma: no cover - scheduler is optional during testing
    from spinal_cord import scheduler  # type: ignore[import]
except ModuleNotFoundError:  # pragma: no cover - allow registry tests without scheduler
    scheduler = None  # type: ignore[assignment]

# Names supplied by ``spinal_cord.dorsal_root``.  They are loaded lazily so that
# importing :mod:`spinal_cord` succeeds even in environments that only have the
# scheduler available or that execute tests directly from the package
# directory.  ``__getattr__`` below resolves these attributes on demand and
# caches them in ``globals()`` for subsequent lookups.
_DORSAL_ROOT_EXPORTS: Dict[str, str] = {
    "afferent_fire": "afferent_fire",
    "EVENT_SOURCE": "EVENT_SOURCE",
    "FIBER_VELOCITIES_M_PER_S": "FIBER_VELOCITIES_M_PER_S",
    "SymbolicEventRouter": "SymbolicEventRouter",
    "ThalamusStub": "ThalamusStub",
    "BrainstemStub": "BrainstemStub",
}

if TYPE_CHECKING:  # pragma: no cover - import only for static analysis
    from .dorsal_root import (  # noqa: F401
        BrainstemStub as _BrainstemStub,
        EVENT_SOURCE as _EVENT_SOURCE,
        FIBER_VELOCITIES_M_PER_S as _FIBER_VELOCITIES_M_PER_S,
        SymbolicEventRouter as _SymbolicEventRouter,
        ThalamusStub as _ThalamusStub,
        afferent_fire as _afferent_fire,
    )


def _load_from_dorsal_root(name: str) -> Any:
    module = import_module(f"{__name__}.dorsal_root")
    attribute = getattr(module, _DORSAL_ROOT_EXPORTS[name])
    globals()[name] = attribute
    return attribute


def __getattr__(name: str) -> Any:
    if name in _DORSAL_ROOT_EXPORTS:
        return _load_from_dorsal_root(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> Iterable[str]:
    return sorted({*globals(), *_DORSAL_ROOT_EXPORTS})


class Brainstem:
    def __init__(self, thalamus, limbic_system, cerebellum, hippocampus, audit_logger, basal_ganglia):
        self.thalamus = thalamus
        self.limbic_system = limbic_system
        self.cerebellum = cerebellum
        self.hippocampus = hippocampus
        self.audit_logger = audit_logger
        self.basal_ganglia = basal_ganglia

        print("[Brainstem] Initialized with all core components.")

    def process_signal(self, input_signal):
        thalamus_output = self.thalamus.score_signal(input_signal)
        limbic_response = self.limbic_system.evaluate_signal(thalamus_output)
        action = self.basal_ganglia.evaluate_decision(limbic_response)
        self.cerebellum.execute_action(action)
        self.audit_logger.log({
            "input": input_signal,
            "thalamus_output": thalamus_output,
            "limbic_response": limbic_response,
            "action": action
        })