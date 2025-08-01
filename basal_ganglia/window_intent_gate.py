import json
import os
from datetime import datetime, timezone
import pygetwindow as gw

WINDOW_DIR_PATH = os.path.join(os.path.dirname(__file__), "../optic_nerve/window_directory.json")


def load_window_directory():
    with open(WINDOW_DIR_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def match_window_to_directory(directory, active_windows):
    best_match = None
    highest_score = -1

    for window in active_windows:
        for entry in directory:
            score = sum(kw.lower() in window.title.lower() for kw in entry["match_keywords"])
            if score > highest_score:
                highest_score = score
                best_match = {
                    "label": entry["label"],
                    "title": window.title,
                    "bounding_box": {
                        "left": window.left,
                        "top": window.top,
                        "width": window.width,
                        "height": window.height
                    },
                    "priority": entry.get("priority", 0),
                    "allowed_actions": entry.get("allowed_actions", []),
                    "requires_toggle": entry.get("requires_toggle", False)
                }

    return best_match


def gate_window_switch(intent_obj, audit_logger=None):
    if intent_obj.get("intent") != "switch_to":
        return None

    directory = load_window_directory()
    windows = gw.getWindowsWithTitle("")

    matched = match_window_to_directory(directory, windows)
    if not matched:
        result = {
            "status": "inhibited",
            "reason": "no_matching_window",
            "intent": intent_obj
        }
    else:
        result = {
            "status": "approved",
            "matched_window": matched,
            "intent": intent_obj
        }

    # Symbolic log
    if audit_logger:
        audit_logger.log_output({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "window_switch_intent",
            "input": intent_obj,
            "output": result
        })

    return result
