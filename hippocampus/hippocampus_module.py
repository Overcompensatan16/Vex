import json
import os
import sys
from datetime import datetime, timezone
from memory.memory_store_factory import MemoryStoreFactory
from audit.audit_logger_factory import AuditLoggerFactory
from cerebral_cortex.temporal_lobe.context_tracker import ContextTracker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def derive_priority(tags):
    priority = 0
    if "meta_reasoning" in tags:
        priority += 5
    if "tarot" in tags:
        priority += 10
    for tag in tags:
        if tag.startswith("priority_weight:"):
            try:
                explicit_priority = int(tag.split(":")[1])
                priority = max(priority, explicit_priority)
                break
            except ValueError:
                pass
    return priority


class HippocampusModule:
    def __init__(
            self,
            max_facts: int = 1000,
            context_size: int = 10,
            memory_factory: MemoryStoreFactory | None = None,
            external_memory_path: str | None = None,
    ) -> None:
        self.max_facts = max_facts
        self.facts: list[dict] = []
        self.indexes = {"tags": {}, "trump": {}, "suit": {}}
        self.logger = AuditLoggerFactory("hippocampus")
        self.context = ContextTracker(max_size=context_size)
        self.memory_factory = memory_factory or MemoryStoreFactory(
            base_dir=r"E:\AI_Memory_Stores"
        )
        self.external_memory_path = (
                external_memory_path or r"E:\AI_Memory_Stores\general_facts.jsonl"
        )
        dir_path = os.path.dirname(self.external_memory_path) or "."
        os.makedirs(dir_path, exist_ok=True)

    self.category_paths = {
        "general": os.path.join(dir_path, "general_facts.jsonl"),
        "opinions": os.path.join(dir_path, "opinions.jsonl"),
        "math": os.path.join(dir_path, "math_facts.jsonl"),
        "emotion": os.path.join(dir_path, "emotion_facts.jsonl"),
        "history": os.path.join(dir_path, "historical_facts.jsonl"),
        "science": os.path.join(dir_path, "science_facts.jsonl"),
        "philosophy": os.path.join(dir_path, "philosophy_facts.jsonl"),
        "technology": os.path.join(dir_path, "technology_facts.jsonl"),
        "biography": os.path.join(dir_path, "biography_facts.jsonl"),
        "geography": os.path.join(dir_path, "geography_facts.jsonl"),
        "culture": os.path.join(dir_path, "culture_facts.jsonl"),
        "physics": os.path.join(dir_path, "physics_facts.jsonl"),
        "chemistry": os.path.join(dir_path, "chemistry_facts.jsonl"),
        "chemistry_external": os.path.join("external_store", "chemistry.jsonl"),
        "compounds": os.path.join(dir_path, "known_compounds.jsonl"),
        "linguistic": os.path.join(dir_path, os.path.basename(self.external_memory_path)),
    }

    def _update_indexes(self, fact: dict) -> None:
        for tag in fact.get("tags", []):
            self.indexes["tags"].setdefault(tag, []).append(fact)
        tarot = fact.get("tarot", {})
        trump = tarot.get("trump") or fact.get("trump")
        suit = tarot.get("suit") or fact.get("suit")
        if trump:
            self.indexes["trump"].setdefault(trump, []).append(fact)
        if suit:
            self.indexes["suit"].setdefault(suit, []).append(fact)

    @staticmethod
    def _infer_category(fact: dict) -> str:
        tags = fact.get("tags", [])
        rec_type = fact.get("type") or fact.get("fact_type")
        if "math" in tags or rec_type in ("math_conclusion", "math"):
            return "math"
        if "pain" in tags or rec_type == "pain":
            return "pain"
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
        return "linguistic"

    def _append_external_memory(self, fact: dict, category: str) -> None:
        try:
            path = self.category_paths.get(category, self.category_paths["linguistic"])
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(fact) + "\n")
            if category == "chemistry":
                extra = self.category_paths.get("chemistry_external")
                os.makedirs(os.path.dirname(extra), exist_ok=True)
                with open(extra, "a", encoding="utf-8") as ef:
                    ef.write(json.dumps(fact) + "\n")
            self.logger.log_event("write_success", {"category": category, "path": path})
        except Exception as e:
            self.logger.log_error("external_memory_write_failed", {"error": str(e), "category": category})

    def store_record(self, fact: dict, category: str | None = None) -> None:
        if not isinstance(fact, dict):
            raise ValueError("record must be a dict")
        if "timestamp" not in fact:
            fact["timestamp"] = datetime.now(timezone.utc).isoformat()
        if "priority_weight" not in fact:
            fact["priority_weight"] = derive_priority(fact.get("tags", []))
        self.facts.append(fact)
        self._update_indexes(fact)
        if len(self.facts) > self.max_facts:
            self.facts.pop(0)
        self.logger.log_event("store_record", {"summary": fact.get("fact", "")[:75]})
        self.context.add(fact)

        cat = category or self._infer_category(fact)
        self._append_external_memory(fact, cat)

        if self.memory_factory:
            module_name = fact.get("source", "generic")
            writer = self.memory_factory.get_memory_writer(module_name, cat)
            writer.append(fact)

    def store_math_fact(self, parietal_result: dict) -> None:
        conclusion = parietal_result.get("conclusion")
        confidence = parietal_result.get("confidence", 1.0)
        connections = parietal_result.get("connections", [])
        timestamp = parietal_result.get("timestamp")
        math_record = {
            "fact": f"Math conclusion: {conclusion}",
            "type": "math_conclusion",
            "tarot": {"trump": None, "suit": "Pentacles"},
            "source": "parietal_lobe",
            "credibility": confidence,
            "tags": ["math", "structural_reasoning"],
            "connections": connections,
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        }
        self.store_record(math_record, category="math")
        summary = (conclusion[:75] + "...") if conclusion and len(conclusion) > 75 else conclusion
        self.logger.log_event("store_math_fact", {"summary": summary})

    def update_fact_credibility(self, fact_str: str, new_credibility: float) -> bool:
        for fact in self.facts:
            if fact["fact"] == fact_str:
                fact["credibility"] = new_credibility
                summary = (fact_str[:50] + "...") if len(fact_str) > 50 else fact_str
                self.logger.log_event(
                    "update_credibility",
                    {"summary": summary, "credibility": new_credibility},
                )
                return True
        return False

    def query_facts(self, query_tags: list[str] = None) -> list[dict]:
        if not query_tags:
            return self.facts.copy()
        results = []
        for tag in query_tags:
            results.extend(self.indexes["tags"].get(tag, []))
        return results
