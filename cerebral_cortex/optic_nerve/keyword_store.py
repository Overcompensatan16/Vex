import json
import os
import uuid

KEYWORD_STORE_PATH = os.path.join(os.path.dirname(__file__), "keyword_store.jsonl")


def load_keyword_store():
    try:
        with open(KEYWORD_STORE_PATH, "r", encoding="utf-8") as f:
            return [json.loads(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[WARN] Keyword store not found at {KEYWORD_STORE_PATH}. Creating new.")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to load keyword store: {e}")
        return []


def save_keyword_entry(new_entry):
    try:
        with open(KEYWORD_STORE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(new_entry, ensure_ascii=False) + "\n")
        print(f"[INFO] Added new keyword entry: {new_entry['label']}")
    except Exception as e:
        print(f"[ERROR] Failed to save keyword entry: {e}")


def generate_keyword_entry(text):
    return {
        "label": f"auto_{uuid.uuid4().hex[:8]}",
        "keywords": [text.strip()],
        "actions": [{"type": "tag", "target": "unknown"}],
        "context": ["auto_generated"],
        "priority": 6.1,
        "added_by": "autogen",
        "timestamp": datetime.now(ZoneInfo("UTC")).isoformat()
    }


def find_matching_keywords(text, keyword_list):
    matches = []
    for keyword_entry in keyword_list:
        for word in keyword_entry.get("keywords", []):
            if word.lower() in text.lower():
                matches.append(keyword_entry)
                break
    return matches


def update_store_with_new_keywords(text):
    new_entry = generate_keyword_entry(text)
    save_keyword_entry(new_entry)


def infer_intent_from_text(text, keyword_list=None):
    if keyword_list is None:
        keyword_list = load_keyword_store()

    matches = find_matching_keywords(text, keyword_list)
    if matches:
        return matches[0]

    update_store_with_new_keywords(text)
    return None
