"""Recruitment order tests for the ventral horn motor pool."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from spinal_cord.ventral_horn import MotorPool


def test_henneman_size_principle() -> None:
    pool = MotorPool("biceps_brachii", region="right_arm", antagonist_name="triceps_brachii")

    drive_schedule = [
        (5.0, 0.35),
        (15.0, 0.5),
        (25.0, 0.7),
        (35.0, 0.9),
        (45.0, 1.1),
    ]

    for time, weight in drive_schedule:
        pool.receive({"t": time, "source": "dorsal_horn", "fiber": "WDR", "weight": weight})
        pool.step_until(time + 5.0)

    first_spike_times = []
    for neuron in pool.alpha_mns:
        first_spike_times.append(neuron.spike_times[0] if neuron.spike_times else None)

    assert all(time is not None for time in first_spike_times), "All motor units should recruit"

    filtered = [time for time in first_spike_times if time is not None]
    assert filtered == sorted(filtered), "Recruitment should follow size order"

    state = pool.telemetry()
    assert state.alpha_spikes[0]
    assert state.alpha_rates[0] >= state.alpha_rates[-1]
