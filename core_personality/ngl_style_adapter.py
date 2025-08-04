"""Simple style adjustments for NGL output."""


def apply_style(sentence: str, metadata: dict) -> str:
    """Return sentence with style modifiers applied."""
    style = (metadata.get("personality_style") or "neutral").lower()
    if style == "scholarly":
        return sentence
    if style == "playful":
        return sentence.replace(".", "!")
    if style == "dramatic":
        return sentence.upper()
    return sentence


__all__ = ["apply_style"]
