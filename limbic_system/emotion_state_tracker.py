"""Provide symbolic emotion tags for the NGL."""

EMOTIONS = ["neutral", "curious", "intense", "reflective"]

_current = 0


def get_emotional_tag() -> str:
    """Return a cycling emotional tag for demonstration."""
    global _current
    tag = EMOTIONS[_current % len(EMOTIONS)]
    _current += 1
    return tag


__all__ = ["get_emotional_tag"]
