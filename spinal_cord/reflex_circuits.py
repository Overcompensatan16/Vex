"""Canonical spinal reflex circuit definitions."""

from __future__ import annotations

from typing import Sequence

from spinal_cord.reflex_types import (
    DorsalHornReflex,
    ProprioEvent,
    ReflexContext,
    ReflexRule,
)


def withdrawal_circuit(ctx: ReflexContext) -> ReflexRule:
    """Return the ipsilateral flexor withdrawal reflex rule."""

    region = ctx.region
    config = ctx.region_config
    flexor = config.get("flexor", "flexor")
    extensor = config.get("extensor", "extensor")
    joint = config.get("joint", "joint")

    def when(local_ctx: ReflexContext) -> bool:
        event = local_ctx.event
        if not isinstance(event, DorsalHornReflex):
            return False
        fiber = event.fiber.lower()
        return (
            event.label == "withdrawal"
            and fiber in {"aδ", "ad", "c"}
            and (event.weight + 0.1) > local_ctx.analgesia
        )

    def gain(local_ctx: ReflexContext) -> float:
        analgesia = _clamp_unit(local_ctx.analgesia)
        base = 0.6 + 0.5 * local_ctx.event.weight - 0.5 * analgesia
        return _clamp_unit(base)

    outputs: Sequence[dict] = (
        {
            "muscle": flexor,
            "mode": "+",
            "scale": 1.0,
        },
        {
            "muscle": extensor,
            "mode": "-",
            "scale": 1.0,
        },
    )

    signals: Sequence[dict] = (
        {
            "path": f"{region}.{flexor}.contraction",
            "map": lambda _, level: level,
        },
        {
            "path": f"{region}.{extensor}.inhibition",
            "map": lambda _, level: level,
        },
        {
            "path": f"{region}.{joint}.flexion_intent",
            "map": lambda _, level: level,
        },
    )

    return ReflexRule(
        name="flexor_withdrawal",
        when=when,
        gain=gain,
        latency_ms=20.0,
        duration_ms=120.0,
        outputs=outputs,
        gates=(lambda local_ctx: not local_ctx.anesthesia,),
        priority=100,
        signals=signals,
    )


def stretch_circuit(ctx: ReflexContext) -> ReflexRule:
    """Return the monosynaptic stretch reflex rule (Ia fibres)."""

    event = ctx.event
    if not isinstance(event, ProprioEvent):
        raise TypeError("stretch_circuit requires a ProprioEvent context")

    region = ctx.region
    agonist = event.muscle
    antagonist = event.antagonist

    def when(local_ctx: ReflexContext) -> bool:
        ev = local_ctx.event
        return isinstance(ev, ProprioEvent) and ev.kind == "Ia" and ev.magnitude > 0.2

    def gain(local_ctx: ReflexContext) -> float:
        mag = _clamp_unit(local_ctx.event.magnitude)
        return _clamp_unit(0.3 + 0.7 * mag)

    outputs: Sequence[dict] = (
        {"muscle": agonist, "mode": "+", "scale": 1.0},
        {"muscle": antagonist, "mode": "-", "scale": 0.8},
    )

    signals: Sequence[dict] = (
        {
            "path": f"{region}.{agonist}.activation",
            "map": lambda _, level: level,
        },
        {
            "path": f"{region}.{antagonist}.inhibition",
            "map": lambda _, level: 0.8 * level,
        },
    )

    return ReflexRule(
        name="monosynaptic_stretch",
        when=when,
        gain=gain,
        latency_ms=6.0,
        duration_ms=60.0,
        outputs=outputs,
        gates=(lambda local_ctx: not local_ctx.anesthesia,),
        priority=60,
        signals=signals,
    )


def crossed_extensor_circuit(ctx: ReflexContext) -> ReflexRule:
    """Return the crossed-extensor reflex rule for contralateral support."""

    config = ctx.region_config.get("crossed_extensor", {})
    target_region = config.get("region", ctx.region)
    extensor = config.get("extensor", "extensor")
    flexor = config.get("flexor", "flexor")
    joint = config.get("joint", "joint")

    def when(local_ctx: ReflexContext) -> bool:
        event = local_ctx.event
        if not isinstance(event, DorsalHornReflex):
            return False
        fiber = event.fiber.lower()
        return event.label == "withdrawal" and fiber in {"aδ", "ad", "c"}

    def gain(local_ctx: ReflexContext) -> float:
        analgesia = _clamp_unit(local_ctx.analgesia)
        base = 0.5 + 0.4 * local_ctx.event.weight - 0.4 * analgesia
        return _clamp_unit(base)

    outputs: Sequence[dict] = (
        {"muscle": extensor, "mode": "+", "scale": 0.9, "region": target_region},
        {"muscle": flexor, "mode": "-", "scale": 0.6, "region": target_region},
    )

    signals: Sequence[dict] = (
        {
            "path": f"{target_region}.{extensor}.activation",
            "map": lambda _, level: 0.9 * level,
        },
        {
            "path": f"{target_region}.{flexor}.inhibition",
            "map": lambda _, level: 0.6 * level,
        },
        {
            "path": f"{target_region}.{joint}.extension_intent",
            "map": lambda _, level: level,
        },
    )

    return ReflexRule(
        name="crossed_extensor",
        when=when,
        gain=gain,
        latency_ms=22.0,
        duration_ms=150.0,
        outputs=outputs,
        gates=(lambda local_ctx: not local_ctx.anesthesia,),
        priority=90,
        signals=signals,
    )


def golgi_circuit(ctx: ReflexContext) -> ReflexRule:
    """Return the Golgi tendon organ reflex rule (Ib fibres)."""

    event = ctx.event
    if not isinstance(event, ProprioEvent):
        raise TypeError("golgi_circuit requires a ProprioEvent context")

    region = ctx.region
    agonist = event.muscle
    antagonist = event.antagonist

    def when(local_ctx: ReflexContext) -> bool:
        ev = local_ctx.event
        return isinstance(ev, ProprioEvent) and ev.kind == "Ib" and ev.magnitude > 0.5

    def gain(local_ctx: ReflexContext) -> float:
        mag = max(0.0, local_ctx.event.magnitude - 0.5)
        return _clamp_unit(0.4 + 0.6 * mag)

    outputs: Sequence[dict] = (
        {"muscle": agonist, "mode": "-", "scale": 1.0},
        {"muscle": antagonist, "mode": "+", "scale": 0.6},
    )

    signals: Sequence[dict] = (
        {
            "path": f"{region}.{agonist}.inhibition",
            "map": lambda _, level: level,
        },
        {
            "path": f"{region}.{antagonist}.activation",
            "map": lambda _, level: 0.6 * level,
        },
    )

    return ReflexRule(
        name="golgi_tendon",
        when=when,
        gain=gain,
        latency_ms=8.0,
        duration_ms=80.0,
        outputs=outputs,
        gates=(lambda local_ctx: not local_ctx.anesthesia,),
        priority=80,
        signals=signals,
    )


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


__all__ = [
    "withdrawal_circuit",
    "stretch_circuit",
    "crossed_extensor_circuit",
    "golgi_circuit",
]
