"""Common dataclasses shared by the reflex orchestrator components."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Mapping, MutableMapping, Sequence, Union

if TYPE_CHECKING:  # pragma: no cover - only for type checking
    from spinal_cord.signal_registry import SignalRegistry  # noqa: F401


@dataclass(frozen=True)
class DorsalHornReflex:
    t: float
    region: str
    label: str
    fiber: str
    weight: float
    mod: Optional[float] = None


@dataclass(frozen=True)
class ProprioEvent:
    t: float
    region: str
    kind: str
    muscle: str
    antagonist: str
    magnitude: float


@dataclass(frozen=True)
class DescendEvent:
    t: float
    region: str
    mode: str
    gain: float


@dataclass
class ReflexContext:
    event: Union[DorsalHornReflex, ProprioEvent, DescendEvent]
    region: str
    registry: "SignalRegistry"
    analgesia: float = 0.0
    anesthesia: bool = False
    region_state: MutableMapping[str, Any] = field(default_factory=dict)
    region_config: Mapping[str, Any] = field(default_factory=dict)
    descend_gain: float = 1.0


GateFn = Callable[[ReflexContext], bool]
EvalFn = Callable[[ReflexContext], float]
Predicate = Callable[[ReflexContext], bool]


@dataclass
class ReflexRule:
    name: str
    when: Predicate
    gain: EvalFn
    latency_ms: float
    duration_ms: float
    outputs: Sequence[Mapping[str, Any]]
    gates: Sequence[GateFn] = field(default_factory=list)
    priority: int = 0
    signals: Sequence[Mapping[str, Any]] = field(default_factory=list)
