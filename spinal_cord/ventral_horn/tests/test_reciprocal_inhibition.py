"""Reciprocal inhibition coordination tests."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from spinal_cord.ventral_horn import MotorPool


def test_antagonist_suppression() -> None:
    biceps = MotorPool("biceps_brachii", region="right_arm", antagonist_name="triceps_brachii")
    triceps = MotorPool("triceps_brachii", region="right_arm", antagonist_name="biceps_brachii")

    biceps.attach_antagonist(triceps)
    triceps.attach_antagonist(biceps)

    for step in range(6):
        time = 10.0 * step
        biceps.receive({"t": time, "source": "dorsal_horn", "fiber": "WDR", "weight": 0.95})
        biceps.step_until(time + 5.0)
        triceps.step_until(time + 5.0)

    biceps.step_until(80.0)
    triceps.step_until(80.0)
    biceps_state = biceps.telemetry()
    triceps_state = triceps.telemetry()
    assert triceps_state.net_drive < 0.0
    assert biceps_state.net_drive >= 0.0
    assert triceps_state.reciprocal_inhibition > 0.0

    for step in range(6, 12):
        time = 10.0 * step
        triceps.receive({"t": time, "source": "dorsal_horn", "fiber": "WDR", "weight": 0.95})
        triceps.step_until(time + 5.0)
        biceps.step_until(time + 5.0)

    biceps.step_until(150.0)
    triceps.step_until(150.0)
    triceps_state = triceps.telemetry()
    biceps_state = biceps.telemetry()
    assert biceps_state.net_drive < 0.0
    assert triceps_state.net_drive >= 0.0
    assert biceps_state.reciprocal_inhibition > 0.0
