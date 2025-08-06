"""Unit tests for TemporalLobe input handling and logging."""

import json
import types
import sys
from pathlib import Path
from cerebral_cortex.temporal_lobe import TemporalLobe

import importlib.util

# --- Stub heavy optional dependencies before importing TemporalLobe ---


class _DummyDoc:
    sents = []


class _DummyNLP:
    def __call__(self, text):  # pragma: no cover - simple stub
        return _DummyDoc()


sys.modules.setdefault(
    "spacy",
    types.SimpleNamespace(
        load=lambda name: _DummyNLP(),
        cli=types.SimpleNamespace(download=lambda name: None),
    ),
)
sys.modules.setdefault("pyautogui", types.SimpleNamespace())
sys.modules.setdefault("pygetwindow", types.SimpleNamespace(getWindowsWithTitle=lambda title: []))

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


_spec = importlib.util.spec_from_file_location("_symbolic_signal", ROOT / "symbolic_signal.py")
_module = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_module)
SymbolicSignal = _module.SymbolicSignal


def _make_temporal_lobe(tmp_path):
    log_path = tmp_path / "log.jsonl"
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"audit_log_path": str(log_path)}))
    tl = TemporalLobe(config_path=str(config_path))
    return tl, log_path


def _read_transform_entry(log_path):
    with open(log_path, "r", encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]
    return next(e for e in entries if e["type"] == "transformer_normalization")


def test_process_dict(tmp_path):
    tl, log_path = _make_temporal_lobe(tmp_path)
    tl.process({"text": "hello", "modality": "dict_mod", "source": "dict_src"})
    entry = _read_transform_entry(log_path)
    assert entry["data"]["tag"] == "dict_mod"
    assert entry["data"]["source"] == "dict_src"


def test_process_string(tmp_path):
    tl, log_path = _make_temporal_lobe(tmp_path)
    tl.process("hello world")
    entry = _read_transform_entry(log_path)
    assert entry["data"]["tag"] == "audio"
    assert entry["data"]["source"] == "temporal_lobe"


def test_process_symbolic_signal(tmp_path):
    tl, log_path = _make_temporal_lobe(tmp_path)
    sig = SymbolicSignal(data={"text": "hey"}, modality="sig_mod", source="sig_src")
    tl.process(sig)
    entry = _read_transform_entry(log_path)
    assert entry["data"]["tag"] == "sig_mod"
    assert entry["data"]["source"] == "sig_src"
    