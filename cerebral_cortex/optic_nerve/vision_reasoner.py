import datetime
from cerebral_cortex.optic_nerve.keyword_store import (
    load_keyword_store,
    find_matching_keywords,
)
from symbolic_signal import SymbolicSignal


def reason_screen(parsed_screen):
    """Enhance parsed screen data with symbolic interpretation."""

    # ``parsed_screen`` may be a ``SymbolicSignal`` or a plain ``dict``. Handle
    # both cases robustly.
    if isinstance(parsed_screen, SymbolicSignal):
        screen_data = parsed_screen.data
        timestamp = parsed_screen.timestamp
    elif isinstance(parsed_screen, dict):
        screen_data = parsed_screen
        timestamp = parsed_screen.get("timestamp")
    else:
        screen_data = getattr(parsed_screen, "data", {})
        timestamp = getattr(
            parsed_screen,
            "timestamp",
            datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )

    keyword_entries = load_keyword_store()
    raw_blocks = screen_data.get("raw_text_blocks", []) if isinstance(screen_data, dict) else []
    interpreted = []

    for text_block in raw_blocks:
        text = text_block.get("text", "")
        matches = find_matching_keywords(text, keyword_entries)

        if matches:
            best_match = max(matches, key=lambda m: m.get("priority", 0.5))
            interpreted_block = {
                **text_block,
                "matches": matches,
                "intent": best_match["label"],
                "primary_action": (
                    best_match["actions"][0]
                    if best_match.get("actions")
                    else None
                ),
                "priority": best_match.get("priority", 0.5)
            }
        else:
            interpreted_block = text_block  # unchanged if no match

        interpreted.append(interpreted_block)

    return {
        "timestamp": timestamp,
        "interpreted_blocks": interpreted,
        "raw_blocks": raw_blocks,
    }
