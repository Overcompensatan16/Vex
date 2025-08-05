import json
import os
import hashlib
from datetime import datetime, timezone
from typing import Dict, Optional, Iterable, Set, Tuple


def classify_fact(fact: dict) -> str:
    subject = fact.get("subject", "").lower()
    predicate = fact.get("predicate", "").lower()
    source = fact.get("source", "").lower()
    tags = fact.get("tags", [])
    rec_type = fact.get("type", "").lower()
    # Recognise fully qualified types or sources present in the config
    if rec_type in FACT_OUTPUT_PATHS:
        return rec_type
    if source in FACT_OUTPUT_PATHS:
        return source

    # Source specific handling (e.g. Wikipedia namespaces)
    if source.startswith("wiki"):
        if rec_type and f"wiki.{rec_type}" in FACT_OUTPUT_PATHS:
            return f"wiki.{rec_type}"
        return "wiki.general"

    # Expand simple types into domain-prefixed keys
    for prefix in (
        "physics",
        "math",
        "cs",
        "quant_bio",
        "quant_finance",
        "statistics",
        "eess",
        "economics",
    ):
        candidate = f"{prefix}.{rec_type}"
        if candidate in FACT_OUTPUT_PATHS:
            return candidate

    # Prioritize tags or type if clearly marked
    if rec_type in {"math", "algebra", "geometry"} or "math" in tags:
        return "math"
    if rec_type == "emotion" or "emotion" in tags:
        return "emotion"
    if rec_type == "opinion" or "opinion" in tags:
        return "opinions"
    if rec_type == "history" or "history" in tags or source.startswith("wiki.historical"):
        return "history"
    if rec_type == "science" or "science" in tags:
        return "science"
    if rec_type == "physics" or "physics" in tags:
        return "physics"
    if rec_type == "chemistry" or "chemistry" in tags or "compound" in fact.get("subtype", ""):
        return "chemistry"
    if rec_type == "technology" or "technology" in tags:
        return "technology"
    if rec_type == "philosophy" or "philosophy" in tags:
        return "philosophy"
    if rec_type == "biography" or "biography" in tags:
        return "biography"
    if rec_type == "geography" or "geography" in tags:
        return "geography"
    if rec_type == "culture" or "culture" in tags:
        return "culture"
    if rec_type == "cs.ai" or "ai" in tags or "neural" in predicate:
        return "cs.ai"

    # Fallback rules
    if "algebra" in subject or "algebra" in predicate:
        return "math.algebra"
    if "quantum" in subject or "entanglement" in predicate:
        return "physics.quantum"

    return "general"

# Path configuration for routed fact output files


_FACT_CONFIG_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "memory", "fact_memory_config.json")
)

# Default base directory used when specific paths are missing from the
# configuration. Mirrors the value used in :class:`FactRouter`.
_DEFAULT_BASE_DIR = os.path.normpath(os.getenv("MEMORY_BASE", r"E:\\AI_Memory_Stores"))


def _load_fact_output_paths(config_path: str) -> Dict[str, str]:
    """Load and normalise fact output paths from ``config_path``.

    Each path is normalised with :func:`os.path.normpath` and its directory is
    created with :func:`os.makedirs` (``exist_ok=True``) to ensure that routing
    helpers can safely write to the target locations.
    """

    try:
        with open(config_path, "r", encoding="utf-8") as fh:
            config = json.load(fh)
    except Exception:
        config = {}

    paths: Dict[str, str] = {}
    for key, raw_path in config.items():
        norm_path = os.path.normpath(raw_path)
        dir_name = os.path.dirname(norm_path)
        try:
            os.makedirs(dir_name, exist_ok=True)
        except OSError:
            pass
        paths[key] = norm_path
    return paths


# Exposed dictionary for routing helpers
FACT_OUTPUT_PATHS: Dict[str, str] = _load_fact_output_paths(_FACT_CONFIG_PATH)


def _ensure_path(key: str, relative: str) -> None:
    """Ensure ``key`` exists in :data:`FACT_OUTPUT_PATHS`.

    ``relative`` is joined to ``_DEFAULT_BASE_DIR`` to construct the path when
    the key is absent from the configuration.
    """

    if key in FACT_OUTPUT_PATHS:
        return
    path = os.path.normpath(os.path.join(_DEFAULT_BASE_DIR, relative))
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except OSError:
        pass
    FACT_OUTPUT_PATHS[key] = path


# Ensure commonly used routes exist even if absent from the config
_ensure_path("emotion", os.path.join("emotion", "facts.jsonl"))
_ensure_path("general", os.path.join("general", "general_facts.jsonl"))

_SEEN_HASHES: Dict[str, Set[str]] = {}


def route_and_write_fact(fact: dict) -> Tuple[bool, str]:
    """Classify ``fact`` and append it to the appropriate JSONL store.

    Returns a tuple ``(stored, path)`` where ``stored`` indicates whether the
    fact was written (``True``) or detected as a duplicate (``False``). ``path``
    will be an empty string if no route could be determined. A warning is
    printed when the destination path is missing.
    """

    key = classify_fact(fact)
    path = FACT_OUTPUT_PATHS.get(key)
    if not path:
        print(f"[route_and_write_fact] Warning: No output path for key '{key}'")
        return False, ""

    payload = json.dumps(fact, sort_keys=True)
    fact_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    seen = _SEEN_HASHES.setdefault(path, set())
    if fact_hash in seen:
        return False, path

    with open(path, "a", encoding="utf-8") as fh:
        fh.write(payload + "\n")
    seen.add(fact_hash)
    return True, path


__all__ = ["FactRouter", "FACT_OUTPUT_PATHS", "route_and_write_fact"]


class FactRouter:
    """Route structured fact records to category-based JSONL stores.

       Parameters
       ----------
       config_path : str | None, optional
           Path to a JSON file mapping category names to output file paths.  The
           file must contain a JSON object where keys are category strings and
           values are the destination JSONL paths, e.g. ``{"general":
           "./general.jsonl"}``. When supplied, this mapping is merged into
           :data:`fact_router.FACT_OUTPUT_PATHS` and overrides any existing
           entries.
       """
    # Base directory for all memory stores.
    _BASE_DIR = os.path.normpath(os.getenv("MEMORY_BASE", r"E:\\AI_Memory_Stores"))

    DEFAULT_ROUTES: Dict[str, str] = {
        "general": os.path.normpath(os.path.join(_BASE_DIR, "general_facts.jsonl")),
        "opinions": os.path.normpath(os.path.join(_BASE_DIR, "opinions.jsonl")),
        "math": os.path.normpath(os.path.join(_BASE_DIR, "math_facts.jsonl")),
        "emotion": os.path.normpath(os.path.join(_BASE_DIR, "emotion_facts.jsonl")),
        "history": os.path.normpath(os.path.join(_BASE_DIR, "historical_facts.jsonl")),
        "science": os.path.normpath(os.path.join(_BASE_DIR, "science_facts.jsonl")),
        "philosophy": os.path.normpath(os.path.join(_BASE_DIR, "philosophy_facts.jsonl")),
        "technology": os.path.normpath(os.path.join(_BASE_DIR, "technology_facts.jsonl")),
        "biography": os.path.normpath(os.path.join(_BASE_DIR, "biography_facts.jsonl")),
        "geography": os.path.normpath(os.path.join(_BASE_DIR, "geography_facts.jsonl")),
        "culture": os.path.normpath(os.path.join(_BASE_DIR, "culture_facts.jsonl")),
        "physics": os.path.normpath(os.path.join(_BASE_DIR, "physics_facts.jsonl")),
        "chemistry": os.path.normpath(os.path.join(_BASE_DIR, "chemistry_facts.jsonl")),
        "compounds": os.path.normpath(os.path.join(_BASE_DIR, "known_compounds.jsonl")),
    }

    def __init__(self, config_path: str | None = None):
        self.routes = self.DEFAULT_ROUTES.copy()
        self.routes.update(FACT_OUTPUT_PATHS)
        self._seen_hashes: Dict[str, Set[str]] = {}

        if config_path:
            try:
                with open(config_path, "r", encoding="utf-8") as fh:
                    config = json.load(fh)
            except Exception:
                config = {}

            if isinstance(config, dict):
                for key, raw_path in config.items():
                    norm_path = os.path.normpath(raw_path)
                    os.makedirs(os.path.dirname(norm_path), exist_ok=True)
                    FACT_OUTPUT_PATHS[key] = norm_path
                    self.routes[key] = norm_path

    @staticmethod
    def infer_category(fact: Dict) -> str:
        rec_type = fact.get("type", "")
        tags = fact.get("tags", [])

        if rec_type == "math" or "math" in tags:
            return "math"
        if rec_type == "opinion" or "opinion" in tags:
            return "opinions"
        if "emotion" in tags or rec_type == "emotion":
            return "emotion"
        if "history" in tags:
            return "history"
        if "science" in tags or rec_type == "science":
            return "science"
        if "physics_related_chemistry" in tags or "physics" in tags or rec_type == "physics":
            return "physics"
        if "chemistry" in tags or rec_type == "chemistry":
            return "chemistry"
        if "philosophy" in tags or rec_type == "philosophy":
            return "philosophy"
        if "technology" in tags or rec_type == "technology":
            return "technology"
        if "biography" in tags or rec_type == "biography":
            return "biography"
        if "geography" in tags or rec_type == "geography":
            return "geography"
        if "culture" in tags or rec_type == "culture":
            return "culture"
        return "general"

    def _load_seen_hashes(self, path: str) -> Set[str]:
        if path in self._seen_hashes:
            return self._seen_hashes[path]

        seen = set()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            fact = json.loads(line)
                            payload = json.dumps(fact, sort_keys=True)
                            fact_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
                            seen.add(fact_hash)
            except Exception:
                pass  # fallback: assume nothing was seen

        self._seen_hashes[path] = seen
        return seen

    def _save_seen_hashes(self, path: str):
        # Optional: persist seen hashes to disk if needed
        pass

    def route_fact(self, fact: Dict, category: Optional[str] = None) -> Tuple[bool, str]:
        """Route ``fact`` to its category file.

        Returns a tuple ``(stored, path)`` where ``stored`` is ``True`` if the
        fact was written and ``False`` if it was detected as a duplicate. The
        ``path`` is the destination file used for routing.
        """
        cat = category or fact.get("type") or fact.get("category") or self.infer_category(fact)
        path = self.routes.get(cat, self.routes.get("general"))
        if not path:
            return False, ""

        fact["_routed"] = datetime.now(timezone.utc).isoformat()
        payload = json.dumps(fact, sort_keys=True)
        fact_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        seen = self._load_seen_hashes(path)
        if fact_hash in seen:
            return False, path

        with open(path, "a", encoding="utf-8") as f:
            f.write(payload + "\n")
        seen.add(fact_hash)
        self._save_seen_hashes(path)
        return True, path

    def load_facts(self, category: str) -> Iterable[Dict]:
        path = self.routes.get(category)
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
