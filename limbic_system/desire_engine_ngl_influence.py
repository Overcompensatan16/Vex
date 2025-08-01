"""Determine NGL motivational tone."""

_TONES = ["informative", "questioning", "commanding"]
_current = 0


def get_active_tone_category() -> str:
    """Cycle through tone categories for demonstration."""
    global _current
    tone = _TONES[_current % len(_TONES)]
    _current += 1
    return tone


__all__ = ["get_active_tone_category"]
