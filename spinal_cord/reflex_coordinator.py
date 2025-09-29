"""Event-driven reflex orchestrator built around the signal registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Sequence, Set

from spinal_cord import scheduler
from spinal_cord.reflex_circuits import (
    crossed_extensor_circuit,
    golgi_circuit,
    stretch_circuit,
    withdrawal_circuit,
)
from spinal_cord.reflex_types import (
    DescendEvent,
    DorsalHornReflex,
    ProprioEvent,
    ReflexContext,
    ReflexRule,
)
from spinal_cord.signal_registry import SignalRegistry


class ReflexArc:
    """Wrapper that resolves a reflex type into concrete circuit rules."""

    _CIRCUITS = {
        "withdrawal": withdrawal_circuit,
        "stretch": stretch_circuit,
        "crossed_extensor": crossed_extensor_circuit,
        "golgi": golgi_circuit,
    }

    def __init__(self, reflex_type: str, context: ReflexContext) -> None:
        if reflex_type not in self._CIRCUITS:
            raise ValueError(f"Unknown reflex type: {reflex_type}")
        self.reflex_type = reflex_type
        self.context = context

    def build_rules(self) -> List[ReflexRule]:
        builder = self._CIRCUITS[self.reflex_type]
        result = builder(self.context)
        if isinstance(result, ReflexRule):
            return [result]
        return list(result)


@dataclass
class MotorOutput:
    region: str
    muscle: str
    level: float
    intent: str


class ReflexOrchestrator:
    """Evaluate reflex rules on events and schedule motor drives/signals."""

    def __init__(
        self,
        motor_bus: Any,
        registry: SignalRegistry,
        *,
        cooldown_ms: float = 50.0,
        activation_floor: float = 0.05,
        drive_priority: float = 0.0,
        signal_priority: float = 0.0,
        region_map: Optional[Mapping[str, Mapping[str, Any]]] = None,
        audit_logger: Optional[Any] = None,
    ) -> None:
        self.motor_bus = motor_bus
        self.registry = registry
        self.cooldown_ms = cooldown_ms
        self.activation_floor = activation_floor
        self.drive_priority = drive_priority
        self.signal_priority = signal_priority
        self._region_map = region_map or {}
        self._audit_logger = audit_logger

        self._region_state: Dict[str, MutableMapping[str, Any]] = {}
        self._cooldowns: Dict[str, tuple[float, int]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def receive(self, event: Any) -> List[ReflexRule]:
        """Process a single spinal cord event."""

        if isinstance(event, DescendEvent):
            self._handle_descend(event)
            return []

        if isinstance(event, (DorsalHornReflex, ProprioEvent)):
            context = self._build_context(event)
            arcs = self._arcs_for_event(event, context)
            if not arcs:
                return []
            candidates: List[ReflexRule] = []
            for arc in arcs:
                for rule in arc.build_rules():
                    if rule.when(context) and all(g(context) for g in rule.gates):
                        candidates.append(rule)

            if not candidates:
                return []

            winners = self._arbitrate(event.t, context, candidates)
            for rule in winners:
                self._activate_rule(rule, context)
            return winners

        raise TypeError(f"Unsupported event type: {type(event)!r}")

    # ------------------------------------------------------------------
    # Event helpers
    # ------------------------------------------------------------------
    def _build_context(self, event: Any) -> ReflexContext:
        region = event.region
        region_state = self._region_state.setdefault(region, {})
        analgesia = float(self.registry.get("system.analgesia.level") or 0.0)
        anesthesia = bool(self.registry.get("system.anesthesia.engaged") or False)
        config = self._region_map.get(region, {})
        descend_gain = region_state.get("descend_gain", 1.0)

        return ReflexContext(
            event=event,
            region=region,
            registry=self.registry,
            analgesia=analgesia,
            anesthesia=anesthesia,
            region_state=region_state,
            region_config=config,
            descend_gain=descend_gain,
        )

    def _handle_descend(self, event: DescendEvent) -> None:
        region_state = self._region_state.setdefault(event.region, {})
        mode = event.mode
        if mode == "gain":
            region_state["descend_gain"] = event.gain
            return
        if mode == "analgesia":
            self.registry.set("system.analgesia.level", event.gain)
            return
            if mode == "anesthesia":
                self.registry.set("system.anesthesia.engaged", bool(event.gain))
            return
        region_state[mode] = event.gain

    @staticmethod
    def _arcs_for_event(event: Any, context: ReflexContext) -> List[ReflexArc]:
        arcs: List[ReflexArc] = []
        if isinstance(event, DorsalHornReflex):
            if event.label == "withdrawal":
                arcs.append(ReflexArc("withdrawal", context))
                if context.region_config.get("crossed_extensor"):
                    arcs.append(ReflexArc("crossed_extensor", context))
        elif isinstance(event, ProprioEvent):
            if event.kind == "Ia":
                arcs.append(ReflexArc("stretch", context))
            elif event.kind == "Ib":
                arcs.append(ReflexArc("golgi", context))
        return arcs

    # ------------------------------------------------------------------
    # Arbitration & scheduling
    # ------------------------------------------------------------------
    def _arbitrate(
        self,
        time_ms: float,
        context: ReflexContext,
        candidates: Sequence[ReflexRule],
    ) -> List[ReflexRule]:
        winners: List[ReflexRule] = []
        selected_priorities: Dict[str, int] = {}

        for rule in sorted(candidates, key=lambda item: item.priority, reverse=True):
            target_regions = self._rule_regions(rule, context.region)
            if not target_regions:
                target_regions = {context.region}

            if not self._rule_allowed(rule, time_ms, target_regions, selected_priorities):
                continue

            winners.append(rule)
            for region in target_regions:
                selected_priorities[region] = max(
                    rule.priority,
                    selected_priorities.get(region, rule.priority),
                )

        return winners

    def _rule_allowed(
        self,
        rule: ReflexRule,
        time_ms: float,
        regions: Set[str],
        selected_priorities: Mapping[str, int],
    ) -> bool:
        for region in regions:
            cooldown = self._cooldowns.get(region)
            if cooldown and time_ms < cooldown[0] and rule.priority < cooldown[1]:
                return False
            prior = selected_priorities.get(region)
            if prior is not None and rule.priority < prior:
                return False
        return True

    def _activate_rule(self, rule: ReflexRule, context: ReflexContext) -> None:
        level = max(0.0, min(1.0, rule.gain(context)))
        if level <= self.activation_floor:
            return

        event_time = context.event.t
        t_on = event_time + rule.latency_ms
        t_off = t_on + rule.duration_ms

        target_regions = set()
        motor_outputs: List[MotorOutput] = []

        for output in rule.outputs:
            muscle = output.get("muscle")
            if not muscle:
                continue
            scale = float(output.get("scale", 1.0))
            mode = output.get("mode", "+")
            direction = 1.0 if mode == "+" else -1.0
            region = output.get("region", context.region)
            target_regions.add(region)

            region_state = self._region_state.setdefault(region, {})
            gain = region_state.get("descend_gain", context.descend_gain if region == context.region else 1.0)
            drive_level = max(-1.0, min(1.0, level * scale * direction * gain))
            motor_outputs.append(MotorOutput(region=region, muscle=muscle, level=drive_level, intent=rule.name))

        for output in motor_outputs:
            scheduler.schedule(
                t_on,
                self.drive_priority,
                self._drive_on,
                output.region,
                output.muscle,
                output.level,
                output.intent,
            )
            scheduler.schedule(
                t_off,
                self.drive_priority,
                self._drive_off,
                output.region,
                output.muscle,
                output.intent,
            )

        for signal in rule.signals:
            path = signal.get("path")
            mapper = signal.get("map")
            if not path or not callable(mapper):
                continue
            value = mapper(context, level)
            self.registry.set(path, value)
            baseline = self._baseline_for(path)
            scheduler.schedule(
                t_off,
                self.signal_priority,
                self._restore_signal,
                path,
                baseline,
                rule.name,
            )

        cooldown_until = t_off + self.cooldown_ms
        for region in target_regions or {context.region}:
            previous = self._cooldowns.get(region)
            if previous is None or cooldown_until >= previous[0] or rule.priority >= previous[1]:
                self._cooldowns[region] = (cooldown_until, rule.priority)

        if self._audit_logger is not None:
            try:
                self._audit_logger.log_event(
                    "reflex_rule_fired",
                    {
                        "rule": rule.name,
                        "region": context.region,
                        "level": level,
                        "t_on": t_on,
                        "t_off": t_off,
                    },
                )
            except Exception:  # pragma: no cover - defensive logging
                pass

    # ------------------------------------------------------------------
    # Scheduler callbacks
    # ------------------------------------------------------------------
    def _drive_on(self, time_ms: float, region: str, muscle: str, level: float, intent: str) -> None:
        self.motor_bus.drive_on(time_ms, region, muscle, level, intent)

    def _drive_off(self, time_ms: float, region: str, muscle: str, intent: str) -> None:
        self.motor_bus.drive_off(time_ms, region, muscle, intent)

    def _restore_signal(self, time_ms: float, path: str, baseline: Any, rule_name: str) -> None:
        self.registry.set(path, baseline)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _baseline_for(self, path: str) -> Any:
        try:
            return self.registry.metadata(path).get("baseline", 0.0)
        except KeyError:
            return 0.0

    @staticmethod
    def _rule_regions(rule: ReflexRule, default_region: str) -> Set[str]:
        regions: Set[str] = set()
        for output in rule.outputs:
            region = output.get("region", default_region)
            regions.add(region)
        return regions


__all__ = ["ReflexArc", "ReflexOrchestrator", "MotorOutput"]
