import re
from dataclasses import dataclass
from typing import Any, Dict, List, MutableMapping, Optional, Tuple, Mapping, Callable

Subscriber = Callable[[str, Any, int, Dict[str, Any], Any], None]

from spinal_cord.reflex_signal_map import REFLEX_REGISTRY


class SignalRegistry:
    _PATH_RE = re.compile(r"^[a-z0-9_]+(?:\.[a-z0-9_]+)*$")

    @dataclass
    class _Entry:
        value: Any = None
        version: int = 0
        meta: Dict[str, Any] = None

        def __post_init__(self) -> None:
            if self.meta is None:
                self.meta = {}

    def __init__(self, audit_logger: Optional[Any] = None) -> None:
        self._entries: Dict[str, SignalRegistry._Entry] = {}
        self._subscribers: List[Tuple[str, Subscriber, Any]] = []
        self._audit_logger = audit_logger

        try:
            from spinal_cord.reflex_signal_map import REFLEX_REGISTRY
            for path, meta in REFLEX_REGISTRY.items():
                self.register(path, dict(meta))
        except ImportError:
            pass

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    def _require_entry(self, path: str) -> _Entry:
        entry = self._entries.get(path)
        if entry is None:
            raise KeyError(f"Signal {path!r} is not registered")
        return entry

    def _validate_path(self, path: str) -> None:
        if not self._PATH_RE.match(path):
            raise ValueError(f"Invalid signal path: {path!r}")

    @staticmethod
    def _clamp(meta: Mapping[str, Any], value: Any) -> Any:
        value_range = meta.get("range") if isinstance(meta, dict) else None
        if value_range is None:
            return value

        lo, hi = value_range
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            clamped = min(max(value, lo), hi)
            return type(value)(clamped) if isinstance(value, int) else clamped
        return value

    @staticmethod
    def _coerce(meta: Mapping[str, Any], value: Any) -> Any:
        signal_type = meta.get("type") if isinstance(meta, dict) else None
        if signal_type in {None, ""}:
            return value
        if value is None:
            return None

        if signal_type in {"analog", "oscillatory"}:
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"Signal type {signal_type!r} requires numeric values, got {type(value)!r}"
                )
            return float(value)

        if signal_type == "digital":
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value
            raise TypeError(
                f"Signal type 'digital' requires bool or enum-string values, got {type(value)!r}"
            )

        if signal_type == "composite":
            if isinstance(value, (str, bool, int, float, dict, list, tuple)):
                return value
            raise TypeError("Signal type 'composite' requires serialisable value types")

        raise ValueError(f"Unknown signal type metadata: {signal_type!r}")

    # ------------------------------------------------------------------
    # Registry methods
    # ------------------------------------------------------------------
    def register(self, path: str, meta: Optional[MutableMapping[str, Any]] = None) -> None:
        """Declare *path* in the registry and optionally attach metadata."""
        self._validate_path(path)
        if path in self._entries:
            return
        self._entries[path] = self._Entry(value=None, version=0, meta=dict(meta) if meta else {})

    def metadata(self, path: str) -> Dict[str, Any]:
        entry = self._require_entry(path)
        return entry.meta

    def set(self, path: str, value: Any) -> Any:
        entry = self._require_entry(path)
        coerced_value = self._coerce(entry.meta, value)
        clamped_value = self._clamp(entry.meta, coerced_value)
        entry.value = clamped_value
        entry.version += 1

        if self._audit_logger:
            self._audit_logger.log_signal(path, clamped_value, entry.version, entry.meta)

        for prefix, subscriber, user_data in self._subscribers:
            if path.startswith(prefix):
                subscriber(path, clamped_value, entry.version, entry.meta, user_data)

        return clamped_value

    def get(self, path: str) -> Any:
        entry = self._require_entry(path)
        return entry.value

    def version(self, path: str) -> int:
        entry = self._require_entry(path)
        return entry.version

    def snapshot(self) -> Dict[str, Tuple[Any, int, Dict[str, Any]]]:
        return {
            path: (entry.value, entry.version, dict(entry.meta))
            for path, entry in self._entries.items()
        }

    def subscribe(self, prefix: str, callback: Subscriber, *, context: Any = None) -> Callable[[], None]:
        """Subscribe to updates for *prefix* and return an unsubscribe handle."""
        self._validate_path(prefix)
        self._subscribers.append((prefix, callback, context))
        return lambda: self._subscribers.remove((prefix, callback, context))

    __all__ = ["SignalRegistry", "REFLEX_REGISTRY"]
