"""Monosynaptic stretch reflex checks."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from spinal_cord.ventral_horn import MotorPool


def test_ia_burst_triggers_alpha_spike() -> None:
    pool = MotorPool("biceps_brachii", region="right_arm", antagonist_name="triceps_brachii")

    pool.receive({"t": 1.0, "source": "Ia", "fiber": "Ia", "weight": 1.2})
    pool.step_until(25.0)

    alpha_spikes = [len(neuron.spike_times) for neuron in pool.alpha_mns]
    assert alpha_spikes[0] > 0

    state = pool.telemetry()
    assert state.renshaw_level > 0.0

    command = pool.emit_command()
    assert command is not None
    assert command.activation > 0.0
    total_spikes = sum(alpha_spikes)
    assert len(command.twitch_events) >= total_spikes
