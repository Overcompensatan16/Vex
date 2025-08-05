import pathlib
import sys
import types
from typing import List, Dict
import importlib.util

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Stub out the heavy ``temporal_lobe`` package to avoid external deps during import
tl_path = ROOT / "cerebral_cortex" / "temporal_lobe"
temporal_lobe_stub = types.ModuleType("cerebral_cortex.temporal_lobe")
temporal_lobe_stub.__path__ = [str(tl_path)]
sys.modules["cerebral_cortex.temporal_lobe"] = temporal_lobe_stub
chemistry_stub = types.ModuleType("cerebral_cortex.temporal_lobe.chemistry_parser")
chemistry_stub.parse_chemistry_text = lambda text: []
sys.modules["cerebral_cortex.temporal_lobe.chemistry_parser"] = chemistry_stub


spec = importlib.util.spec_from_file_location(
    "preprocessor",
    ROOT / "cerebral_cortex" / "source_handlers" / "external_loaders" / "preprocessor.py",
)
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


def _write_tmp_file(tmp_path, name: str = "data.txt") -> str:
    path = tmp_path / name
    path.write_text("dummy")
    return str(path)


def test_dict_block_passes_directly(monkeypatch, tmp_path):
    """Dictionary blocks that already look like facts are stored directly."""

    dummy_fact = {
        "source": "dummy",
        "type": "note",
        "subject": "foo",
        "predicate": "says",
        "value": "bar",
    }

    def dummy_parser(path: str, dump_base: str | None = None) -> List[Dict]:
        return [dummy_fact]

    p.SOURCE_MAP["dummy"] = dummy_parser

    def fake_store_facts(facts):
        fake_store_facts.called_with = list(facts)
        return {"path": {"stored": len(fake_store_facts.called_with)}}

    def fake_generate_facts(*args, **kwargs):  # pragma: no cover - should not run
        raise AssertionError("generate_facts should not be called for dict facts")

    monkeypatch.setattr(p, "store_facts", fake_store_facts)
    monkeypatch.setattr(p, "generate_facts", fake_generate_facts)

    record = {"path": _write_tmp_file(tmp_path), "source": "dummy"}
    res = p.process_record(record)

    assert res["count"] == 1
    assert fake_store_facts.called_with == [dummy_fact]


def test_dict_block_generates_facts(monkeypatch, tmp_path):
    """Dictionary blocks with ``value`` are expanded via ``generate_facts``."""

    block = {"value": "alpha beta.", "type": "cs.AI", "subject": "topic"}

    def dummy_parser(path: str, dump_base: str | None = None) -> List[Dict]:
        return [block]

    p.SOURCE_MAP["dummy2"] = dummy_parser

    captured = {}

    def fake_generate_facts(text, source=None, source_type=None):
        captured["text"] = text
        captured["source_type"] = source_type
        return [{"value": text}]

    stored: List[Dict] = []

    def fake_store_facts(facts):
        stored.extend(facts)
        return {"path": {"stored": len(list(facts))}}

    monkeypatch.setattr(p, "generate_facts", fake_generate_facts)
    monkeypatch.setattr(p, "store_facts", fake_store_facts)

    record = {"path": _write_tmp_file(tmp_path, "file.txt"), "source": "dummy2"}
    res = p.process_record(record)

    assert res["count"] == 1
    assert captured["text"] == "alpha beta."
    assert captured["source_type"] == "cs.AI"
    assert stored == [{"value": "alpha beta.", "subject": "topic"}]


def test_unknown_parser(tmp_path):
    record = {"path": _write_tmp_file(tmp_path, "foo.txt"), "source": "unknown"}
    res = p.process_record(record)
    assert res["count"] == 0
    assert "unknown parser" in res["error"]


def test_wikipedia_alias():
    assert p.SOURCE_MAP.get("wikipedia") is p.SOURCE_MAP.get("wiki")
    