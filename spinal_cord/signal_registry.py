import re
from dataclasses import dataclass
from typing import Any, Dict, List, MutableMapping, Optional, Tuple, Mapping, Callable

Subscriber = Callable[[str, Any, int, Dict[str, Any], Any], None]

import pathlib

from spinal_cord.reflex_indexer import ReflexIndexer


def _resolve_registry_root() -> pathlib.Path:
    """Locate the reflex signal directory on both production and test hosts."""

    default_root = pathlib.Path(r"E:\VexSignalRegistry\reflex_signals")
    if default_root.exists():
        return default_root

    fallback_root = pathlib.Path(__file__).resolve().parents[1] / "VexSignalRegistry" / "reflex_signals"
    if fallback_root.exists():
        return fallback_root

    raise FileNotFoundError(
        "Unable to locate reflex signal registry directory. Checked default path "
        f"{default_root!s} and repository fallback {fallback_root!s}."
    )


_REFLEX_ROOT = _resolve_registry_root()
REFLEX_INDEX = ReflexIndexer(_REFLEX_ROOT)
REFLEX_REGISTRY = dict(REFLEX_INDEX.iter_signal_metadata())


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
            for path, meta in REFLEX_REGISTRY.items():
                self.register(path, dict(meta))
        except ImportError:
            pass
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

        __all__ = ["SignalRegistry", "REFLEX_REGISTRY", "REFLEX_INDEX"]