import json
import os
from datetime import datetime, timezone
from typing import Dict, Optional, Iterable


class FactRouter:
    """Route structured fact records to category-based JSONL stores."""

    DEFAULT_ROUTES: Dict[str, str] = {
        "general": r"E:\\AI_Memory_Stores\\general_facts.jsonl",
        "opinions": r"E:\\AI_Memory_Stores\\opinions.jsonl",
        "math": r"E:\\AI_Memory_Stores\\math_facts.jsonl",
        "emotion": r"E:\\AI_Memory_Stores\\emotion_facts.jsonl",
        "history": r"E:\\AI_Memory_Stores\\historical_facts.jsonl",
        "science": r"E:\\AI_Memory_Stores\\science_facts.jsonl",
        "philosophy": r"E:\\AI_Memory_Stores\\philosophy_facts.jsonl",
        "technology": r"E:\\AI_Memory_Stores\\technology_facts.jsonl",
        "biography": r"E:\\AI_Memory_Stores\\biography_facts.jsonl",
        "geography": r"E:\\AI_Memory_Stores\\geography_facts.jsonl",
        "culture": r"E:\\AI_Memory_Stores\\culture_facts.jsonl",
        "physics": r"E:\\AI_Memory_Stores\\physics_facts.jsonl",
        "chemistry": r"E:\\AI_Memory_Stores\\chemistry_facts.jsonl",
        "compounds": r"E:\\AI_Memory_Stores\\known_compounds.jsonl",
    }

    def __init__(self, config_path: str = "fact_memory_config.json") -> None:
        self.config_path = config_path
        self.routes = self._load_config(config_path)

    def _load_config(self, path: str) -> Dict[str, str]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                routes = json.load(f)
        except Exception:
            routes = self.DEFAULT_ROUTES.copy()
        for key, p in routes.items():
            normalized = os.path.normpath(p.replace("\\", os.sep))
            routes[key] = normalized
            os.makedirs(os.path.dirname(normalized), exist_ok=True)
        return routes

    @staticmethod
    def infer_category(fact: Dict) -> str:
        tags = fact.get("tags", [])
        rec_type = fact.get("type") or fact.get("fact_type")
        if "math" in tags or rec_type in {"math", "math_conclusion"}:
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

    def route_fact(self, fact: Dict, category: Optional[str] = None) -> None:
        cat = category or self.infer_category(fact)
        path = self.routes.get(cat, self.routes.get("general"))
        fact["_routed"] = datetime.now(timezone.utc).isoformat()
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(fact) + "\n")

    def load_facts(self, category: str) -> Iterable[Dict]:
        path = self.routes.get(category)
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
