"""Indexer for reflex signal registry JSON modules.

The registry is stored as a collection of subsystem JSON files located in
``E:\\VexSignalRegistry\\reflex_signals``.  Each file carries top-level
``metadata`` describing the subsystem alongside a ``reflex_arcs`` mapping of
named reflex descriptions.  The :class:`ReflexIndexer` collates those files into
multi-key lookup tables so that downstream modules can query reflexes without
knowing which JSON file provided the data.

The indexer supports three primary views:

* ``by_subsystem`` – mapping from subsystem identifier to the reflex arcs it
  defines.
* ``by_name`` – direct lookup of a reflex arc by its canonical string name.
* ``by_field`` – reverse indexes for stimulus, afferent, integration,
  efferent, and response type descriptors allowing cross-cutting queries such
  as "return all reflexes driven by vagal afferents".

It also exposes the ``system_signal_metadata`` dictionary used to seed the
runtime :class:`~spinal_cord.signal_registry.SignalRegistry` with configurable
signals (e.g. anesthesia toggles, baroreflex set-points).
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, MutableMapping

__all__ = [
    "ReflexArc",
    "ReflexIndexer",
]


@dataclass(frozen=True)
class ReflexArc:
    """Structured reflex arc entry collated from JSON files."""

    name: str
    subsystem: str
    data: Mapping[str, Any]
    source_file: Path

    def get(self, field: str, default: Any = None) -> Any:
        """Proxy ``dict.get`` against the underlying arc data."""

        return self.data.get(field, default)


class ReflexIndexer:
    """Collate reflex subsystem JSON files into multi-key indexes."""

    _FIELD_KEYS = ("stimulus", "afferent", "integration", "efferent", "response_type")

    def __init__(self, root: Path) -> None:
        if not isinstance(root, Path):
            raise TypeError("ReflexIndexer root must be a pathlib.Path instance")
        if not root.exists():
            raise FileNotFoundError(f"Reflex registry directory does not exist: {root}")

        self.root = root
        self.metadata_by_subsystem: Dict[str, Mapping[str, Any]] = {}
        self.by_subsystem: Dict[str, List[ReflexArc]] = {}
        self.by_name: Dict[str, List[ReflexArc]] = {}
        self._field_index: Dict[str, Dict[str, List[ReflexArc]]] = {
            key: {} for key in self._FIELD_KEYS
        }
        self._system_signal_metadata: Dict[str, Dict[str, Any]] = {}
        self._load_files()

    # ------------------------------------------------------------------
    # Data access helpers
    # ------------------------------------------------------------------
    def iter_arcs(self) -> Iterator[ReflexArc]:
        for arcs in self.by_subsystem.values():
            yield from arcs

    @property
    def system_signal_metadata(self) -> Mapping[str, Dict[str, Any]]:
        """Metadata payloads used by the runtime signal registry."""

        return self._system_signal_metadata

    def get_by_subsystem(self, subsystem: str) -> List[ReflexArc]:
        """Return a copy of the arcs registered under *subsystem*."""

        return list(self.by_subsystem.get(subsystem, ()))

    def get_by_name(self, name: str) -> List[ReflexArc]:
        """Return all arcs recorded for *name* across subsystems."""

        return list(self.by_name.get(name, ()))

    def get_by_field(self, field: str, value: str) -> List[ReflexArc]:
        """Return arcs whose *field* contains the provided *value*.

        The lookup is case-insensitive.  If no exact match is found in the
        reverse index the method performs a fallback substring search across the
        requested field.
        """

        field_index = self._field_index.get(field)
        if field_index is None:
            return []

        query = value.casefold()
        direct_matches = field_index.get(query)
        if direct_matches:
            return list(direct_matches)

        # Fallback to substring matching for loosely phrased queries.
        results: List[ReflexArc] = []
        for arc in self.iter_arcs():
            field_value = arc.get(field)
            if isinstance(field_value, str) and query in field_value.casefold():
                results.append(arc)
        return results

    # Convenience wrappers -------------------------------------------------
    def get_by_stimulus(self, stimulus: str) -> List[ReflexArc]:
        return self.get_by_field("stimulus", stimulus)

    def get_by_afferent(self, afferent: str) -> List[ReflexArc]:
        return self.get_by_field("afferent", afferent)

    def get_by_integration_site(self, integration: str) -> List[ReflexArc]:
        return self.get_by_field("integration", integration)

    def get_by_efferent(self, efferent: str) -> List[ReflexArc]:
        return self.get_by_field("efferent", efferent)

    def get_by_response_type(self, response_type: str) -> List[ReflexArc]:
        return self.get_by_field("response_type", response_type)

    def iter_signal_metadata(self) -> Iterable[tuple[str, Dict[str, Any]]]:
        for path, meta in self._system_signal_metadata.items():
            yield path, dict(meta)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_files(self) -> None:
        for path in sorted(self.root.glob("*.json")):
            self._load_file(path)

        for arcs in self.by_subsystem.values():
            arcs.sort(key=lambda arc: arc.name)

    def _load_file(self, path: Path) -> None:
        with path.open(encoding="utf-8") as f:
            payload = json.load(f)

        metadata = payload.get("metadata") or {}
        subsystem = metadata.get("subsystem")
        if not subsystem:
            raise ValueError(f"Missing metadata.subsystem in {path}")

        self.metadata_by_subsystem[subsystem] = metadata

        if "reflex_arcs" in payload:
            self._register_reflex_arcs(subsystem, path, payload["reflex_arcs"])

        # Registry metadata file preserves legacy configurable signals.
        if subsystem == "registry_metadata":
            system_states = payload.get("system_states", {})
            if isinstance(system_states, MutableMapping):
                for state, meta in system_states.items():
                    self._system_signal_metadata[f"system.{state}"] = dict(meta)

    def _register_reflex_arcs(
        self, subsystem: str, path: Path, arcs: Mapping[str, Mapping[str, Any]]
    ) -> None:
        if not isinstance(arcs, Mapping):
            raise TypeError(f"reflex_arcs in {path} must be a mapping")

        bucket = self.by_subsystem.setdefault(subsystem, [])
        for name, data in arcs.items():
            if not isinstance(data, Mapping):
                raise TypeError(
                    f"Reflex arc {name!r} in {path} must be a mapping of descriptors"
                )

            arc = ReflexArc(name=name, subsystem=subsystem, data=dict(data), source_file=path)
            self.by_name.setdefault(name, []).append(arc)
            bucket.append(arc)

            for field in self._FIELD_KEYS:
                self._index_field(field, data.get(field), arc)

    def _index_field(self, field: str, value: Any, arc: ReflexArc) -> None:
        if value is None:
            return

        values: List[str]
        if isinstance(value, str):
            values = [value]
        elif isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
            values = [str(item) for item in value]
        else:
            values = [str(value)]

        field_index = self._field_index[field]
        for item in values:
            normalized = item.casefold()
            field_index.setdefault(normalized, []).append(arc)