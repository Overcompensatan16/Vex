"""Ensure Renshaw feedback curbs runaway activity."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from spinal_cord.ventral_horn import MotorPool


def test_renshaw_feedback_caps_firing() -> None:
    pool = MotorPool("triceps_brachii", region="right_arm", antagonist_name="biceps_brachii")

    for step in range(12):
        time = 5.0 * step
        pool.receive({"t": time, "source": "dorsal_horn", "fiber": "WDR", "weight": 1.2})
        pool.step_until(time + 5.0)

    pool.step_until(120.0)
    state = pool.telemetry()

    assert state.renshaw_level > 0.05
    assert max(state.alpha_rates) < 220.0
    assert state.net_drive < 5.0
