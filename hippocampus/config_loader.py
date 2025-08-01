import json

DEFAULT_CONFIG = {
  "hippocampus": {
    "max_facts": 1000,
    "persistence_path": "memory_store.json",
    "external_memory_path": null,
    "prune_strategy": "priority"
  },
  "reasoning": {
    "mode": "verbose"
  },
  "audit": {
    "log_path": "audit_log.json"
  }
}


def load_config(path="config.json"):
    try:
        with open(path, 'r') as f:
            config = json.load(f)
        print(f"[ConfigLoader] Loaded config from {path}")
        return config
    except FileNotFoundError:
        print(f"[ConfigLoader] Config file not found at {path}. Using default config.")
        return DEFAULT_CONFIG
    except Exception as e:
        print(f"[ConfigLoader] Error loading config: {e}. Using default config.")
        return DEFAULT_CONFIG
