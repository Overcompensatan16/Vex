"""Unit tests for the symbolic cardiac heartbeat module."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from audit.audit_logger_factory import AuditLoggerFactory
from body.torso.cardiac import HeartModule


def _make_audit(tmp_path, name: str) -> AuditLoggerFactory:
    return AuditLoggerFactory(name, log_path=str(tmp_path / f"{name}.jsonl"))


def test_heartbeat_packet_baseline(tmp_path) -> None:
    module = HeartModule(
        rest_rate_bpm=60.0,
        amplitude=1.0,
        variability=0.0,
        coherence=0.2,
        audit_factory=_make_audit(tmp_path, "heart_baseline"),
    )

    packet = module.generate_heartbeat_packet(0.0)
    assert 0.0 <= packet.pulse_signal <= 1.0
    assert packet.phase in {"systole", "diastole"}
    assert packet.heart_rate_current == module.rest_rate_bpm * module.tension_scale * module.fatigue_scale

    packet_next = module.generate_heartbeat_packet(0.5)
    assert 0.0 <= packet_next.pulse_signal <= 1.0
    assert packet_next.heart_rate_current > 0
    assert packet_next.pulse_signal != packet.pulse_signal


def test_tension_fatigue_and_emotion_modulate_rate(tmp_path) -> None:
    module = HeartModule(
        rest_rate_bpm=60.0,
        amplitude=1.0,
        variability=0.0,
        coherence=0.0,
        audit_factory=_make_audit(tmp_path, "heart_modulation"),
    )

    baseline = module.generate_heartbeat_packet(0.0)
    stressed = module.generate_heartbeat_packet(0.5, tension_input=0.5)
    fatigued = module.generate_heartbeat_packet(1.0, fatigue_input=0.3)

    assert stressed.heart_rate_current > baseline.heart_rate_current
    assert fatigued.heart_rate_current < stressed.heart_rate_current

    fear_state = {"valence": -0.8, "arousal": 0.9, "dominance": 0.4}
    emotional = module.generate_heartbeat_packet(1.5, emotion_modulation=fear_state)

    assert emotional.heart_rate_current > fatigued.heart_rate_current
    assert module.last_packet() == emotional.as_dict()

    metadata = module.build_rig_metadata()
    assert metadata["module"] == "heart"
    assert metadata["rig_channels"][0]["name"] == "CTRL_Torso_Heartbeat"
    assert "bp_systolic" in module.afferent_channels
    assert "emotion_modulation" in module.efferent_channels