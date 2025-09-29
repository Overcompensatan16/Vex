"""Tests for the biophysical dorsal horn model."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from spinal_cord.dorsal_horn import process_input


def _count_spikes(spike_train: list[bool]) -> int:
    return sum(1 for fired in spike_train if fired)


def test_touch_signal_prefers_mechanoreceptive_laminae() -> None:
    """Gentle touch should drive laminae III–IV without activating nociceptors."""

    result = process_input(0.3)
    laminae = result["laminae"]

    assert result["overall"] == "maintain_contact"
    assert _count_spikes(laminae["III_IV"]["spikes"]) > 0
    assert _count_spikes(laminae["I"]["spikes"]) == 0
    assert len(laminae["III_IV"]["membrane"]) == len(laminae["I"]["membrane"])


def test_painful_signal_drives_withdrawal_projection() -> None:
    """High intensity stimuli recruit lamina I and WDR neurons to trigger withdrawal."""

    result = process_input({"intensity": 1.1})
    laminae = result["laminae"]

    nociceptive_spikes = _count_spikes(laminae["I"]["spikes"]) + _count_spikes(laminae["V"]["spikes"])
    assert result["overall"] == "withdrawal"
    assert nociceptive_spikes >= 1
    assert result["reflexes"]["withdrawal"] > result["reflexes"]["maintain_contact"]


def test_descending_analgesia_dampens_nociceptive_output() -> None:
    """Descending inhibition should reduce nociceptive spike counts."""

    baseline = process_input({"intensity": 1.0})
    analgesia = process_input({"intensity": 1.0, "descending": "analgesia", "descending_strength": 1.5})

    base_spikes = _count_spikes(baseline["laminae"]["I"]["spikes"]) + _count_spikes(baseline["laminae"]["V"]["spikes"])
    analgesic_spikes = _count_spikes(analgesia["laminae"]["I"]["spikes"]) + _count_spikes(analgesia["laminae"]["V"]["spikes"])

    assert analgesic_spikes <= base_spikes
    assert analgesia["reflexes"]["withdrawal"] <= baseline["reflexes"]["withdrawal"]
