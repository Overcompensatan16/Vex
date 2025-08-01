"""Symbolic Natural Language Generator as described in README."""
from __future__ import annotations
from rephrase_net import neural_rephrase
from typing import Any, Dict

from core_personality.ngl_style_adapter import apply_style
from rephrase_net import neural_rephrase
from limbic_system.emotion_state_tracker import get_emotional_tag
from limbic_system.desire_engine_ngl import get_active_tone_category
from amygdala.amygdala_module import Amygdala


TEMPLATES: Dict[str, Dict[str, str]] = {
    "is": {
        "neutral": "{subject} is {value}.",
        "curious": "Did you know {subject} is {value}?",
        "emotional": "{subject} truly is {value}.",
    },
    "causes": {
        "neutral": "{subject} causes {value}.",
        "intense": "{subject} directly causes {value}!",
        "reflective": "{subject} often leads to {value}.",
    },
}


def apply_confidence_filter(sentence: str, confidence: float) -> str:
    """Return ``sentence`` modified based on ``confidence`` level."""
    if confidence < 0.7:
        return "It might be that " + sentence[0].lower() + sentence[1:]
    if confidence < 0.9:
        return "It seems that " + sentence
    return sentence


def assemble_tone_info() -> Dict[str, str]:
    """Collect tone information from emotion and desire engines."""
    return {
        "emotion": get_emotional_tag(),
        "tone": get_active_tone_category(),
        "personality_style": "scholarly",
    }


def route_to_personality_plugin(sentence: str, metadata: Dict[str, str]) -> str:
    """Apply personality style plugin to ``sentence``."""
    return apply_style(sentence, metadata)


def generate_natural_phrase(fact: dict, tone_info: dict) -> dict:
    if not fact:
        return {"phrase": "I couldn't parse that.", "tags": []}

    # Rephrase value using neural model
    original_value = fact.get("value", "")
    rephrased_value = neural_rephrase(original_value) if original_value else original_value

    template = TEMPLATES.get(fact["predicate"], {}).get(
        tone_info.get("emotion", "neutral"),
        "{subject} is {value}."
    )

    raw_sentence = template.format(
        subject=fact.get("subject", "something"),
        value=rephrased_value
    )

    confidence_adjusted = apply_confidence_filter(raw_sentence, fact.get("confidence", 1.0))
    stylized_output = route_to_personality_plugin(confidence_adjusted, tone_info)

    amygdala = Amygdala()
    input_context = {"tags": [tone_info["emotion"]], "credibility": fact.get("confidence", 0.8)}
    fear_level = amygdala.assess_threat(input_context)
    amygdala.react(fear_level, context={"fact": rephrased_value, "tags": [tone_info["emotion"]]})

    return {
        "phrase": stylized_output,
        "tags": [tone_info["emotion"], tone_info["personality_style"]]
    }
