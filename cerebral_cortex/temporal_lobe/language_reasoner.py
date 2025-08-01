import spacy

# ───────────────────── SpaCy bootstrap ───────────────────── #
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


def process_text(text: str):
    """
    Run SpaCy on `text` and return token/lemma/POS/dependency information
    sentence-by-sentence.
    """
    doc = nlp(text or "")
    results = []
    for sent in doc.sents:
        results.append(
            {
                "text": sent.text,
                "tokens": [t.text for t in sent],
                "lemmas": [t.lemma_ for t in sent],
                "pos": [t.pos_ for t in sent],
                "dependencies": [(t.text, t.dep_, t.head.text) for t in sent],
            }
        )
    return results


def reason_over_screen():
    """
    Capture the screen via OCR (vision_parser.parse_screen), then run full SpaCy
    NLP over each detected text block.
    """
    from cerebral_cortex.optic_nerve.vision_parser import parse_screen

    signal = parse_screen()
    parsed_screen = signal.data if hasattr(signal, "data") else signal
    blocks = parsed_screen.get("raw_text_blocks", [])

    all_reasoned = []
    for block in blocks:
        txt = block.get("text", "")
        if txt:
            all_reasoned.append(
                {
                    "original": txt,
                    "analysis": process_text(txt),
                }
            )

    return {
        "timestamp": parsed_screen.get("timestamp"),
        "screen_analysis": all_reasoned,
        "visible_files": parsed_screen.get("visible_files", []),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(reason_over_screen(), indent=2))
