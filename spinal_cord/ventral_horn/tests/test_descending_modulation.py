"""Descending drive tests."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from spinal_cord.ventral_horn import MotorPool


def test_descending_facilitation_and_anesthesia_gate() -> None:
    pool = MotorPool("biceps_brachii", region="right_arm", antagonist_name="triceps_brachii")

    pool.receive({"t": 10.0, "source": "dorsal_horn", "fiber": "WDR", "weight": 0.35})
    pool.step_until(30.0)
    baseline_spikes = [len(neuron.spike_times) for neuron in pool.alpha_mns]

    pool.receive({"t": 40.0, "source": "corticospinal", "fiber": "desc", "weight": 0.7})
    pool.step_until(45.0)

    pool.receive({"t": 50.0, "source": "dorsal_horn", "fiber": "WDR", "weight": 0.35})
    pool.step_until(80.0)

    facilitated_spikes = [len(neuron.spike_times) for neuron in pool.alpha_mns]
    assert facilitated_spikes[0] > baseline_spikes[0]

    command = pool.emit_command()
    assert command is not None and command.activation > 0.0

    pool.anesthesia.suspend()
    pool.receive({"t": 90.0, "source": "dorsal_horn", "fiber": "WDR", "weight": 0.8})
    pool.step_until(110.0)
    assert pool.emit_command() is None

    pool.anesthesia.resume()
    pool.receive({"t": 120.0, "source": "dorsal_horn", "fiber": "WDR", "weight": 0.8})
    pool.step_until(150.0)
    resumed_command = pool.emit_command()
    assert resumed_command is not None
    assert resumed_command.activation >= command.activation * 0.8
