"""Unit tests for the lungs respiratory module."""

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from body.torso.respiratory import LungsModule


def test_breathing_signal_progresses_through_cycle():
    module = LungsModule(
        rest_rate_bpm=60.0,
        coherence=0.0,
        inhale_exhale_ratio=0.5,
        audit_enabled=False,
    )

    packet_start = module.update(0.0)
    packet_mid_inhale = module.update(0.25)
    packet_peak_inhale = module.update(0.5)
    packet_mid_exhale = module.update(0.75)
    packet_cycle_complete = module.update(1.0)

    assert 0.0 <= packet_start["breathing_signal"] <= 1.0
    assert packet_start["breathing_signal"] < packet_mid_inhale["breathing_signal"] < packet_peak_inhale["breathing_signal"]
    assert packet_peak_inhale["breathing_signal"] > packet_mid_exhale["breathing_signal"] > packet_cycle_complete["breathing_signal"]
    assert packet_cycle_complete["breathing_signal"] == pytest.approx(packet_start["breathing_signal"], abs=1e-6)


def test_afferent_packet_contains_expected_keys():
    module = LungsModule(coherence=0.0, audit_enabled=False)
    packet = module.build_afferent_packet(1.23)
    expected_keys = {
        "respiratory_autonomic.respiratory.breathing_signal",
        "respiratory_autonomic.respiratory.breathing_signal_scaled",
        "respiratory_autonomic.respiratory.breath_rate_current",
        "respiratory_autonomic.respiratory.breath_phase",
        "respiratory_autonomic.respiratory.breath_velocity",
    }
    assert set(packet.keys()) == expected_keys
    assert all(packet[key] is not None for key in expected_keys)