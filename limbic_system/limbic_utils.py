"""Utility helpers for the LimbicSystem."""

BASIC_EMOTIONS = {
    "joy",
    "fear",
    "anger",
    "sadness",
    "anticipation",
    "trust",
    "surprise",
    "disgust",
}


def compute_salience(signal: dict) -> list[str]:
    """Return emotional salience tags derived from ``signal``."""
    tags = signal.get("tags", [])
    return [t for t in tags if t in BASIC_EMOTIONS]


def compute_salience_score(signal: dict) -> dict:
    """Return emotion intensity scores keyed by tag."""
    raw_tags = compute_salience(signal)
    intensities = signal.get("intensity", {})
    return {tag: float(intensities.get(tag, 0.5)) for tag in raw_tags}


def blend_score(emotion_state, affinity: list[str]) -> float:
    """Return emotional valence for a node based on ``emotion_state``."""
    if emotion_state.primary in affinity:
        base = emotion_state.intensity
    else:
        base = 0.0
    for name, weight in getattr(emotion_state, "blends", []):
        if name in affinity:
            base += weight * emotion_state.intensity
    return max(0.0, min(1.0, base))


def check_balance(left_path: list[str], right_path: list[str]) -> float:
    """Return a simple moral tension score between two paths."""
    if not left_path and not right_path:
        return 0.0
    diff = abs(len(left_path) - len(right_path))
    return -diff / max(len(left_path + right_path), 1)

def build_moral_path(signal: dict, sephirot, qliphoth) -> tuple[list[str], list[str]]:
    """Return Sephirot and Qliphoth paths from tags in ``signal``."""
    tags = signal.get("tags", [])
    moral = [t for t in tags if t in getattr(sephirot, "nodes", [])]
    shadow = [t for t in tags if t in getattr(qliphoth, "nodes", [])]
    return moral, shadow


__all__ = [
    "compute_salience",
    "compute_salience_score",
    "build_moral_path",
    "blend_score",
    "check_balance",
]