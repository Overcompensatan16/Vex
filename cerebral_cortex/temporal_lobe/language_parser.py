import re
import time
import pygetwindow as gw
import pyautogui
from cerebral_cortex.temporal_lobe.language_reasoner import process_text


def parse_language(text: str):
    """Return token list and word count for a block of text."""
    tokens = re.findall(r"\b\w+\b", text.lower())
    return {"tokens": tokens, "word_count": len(tokens)}


def reason_language(parsed_lang: dict):
    """Apply deeper NLP reasoning on parsed text using ``language_reasoner``."""
    text = " ".join(parsed_lang.get("tokens", []))
    if not text:
        return []
    return process_text(text)


def get_best_window(target_keywords):
    windows = gw.getWindowsWithTitle('')
    best_match = None
    best_score = -1

    for win in windows:
        title = win.title.lower()
        if not win.visible or not win.width or not win.height:
            continue

        score = sum(kw in title for kw in target_keywords)
        if score > best_score:
            best_score = score
            best_match = win

    if best_match:
        return {
            "left": best_match.left,
            "top": best_match.top,
            "width": best_match.width,
            "height": best_match.height
        }
    return None


def run_ocr_and_detect_intent():
    from cerebral_cortex.optic_nerve.vision_parser import parse_screen

    print("[OCR] Starting screen parse...")
    signal = parse_screen()
    result = signal.data if hasattr(signal, "data") else signal
    print(f"[OCR] Detected text:\n{result}\n")

    # Combine detected blocks into one string for parsing
    text = " ".join(block.get("text", "") for block in result.get("raw_text_blocks", []))
    parsed_lang = parse_language(text)
    if parsed_lang.get("tokens"):
        print("[LANGUAGE PARSER] Parsed:", parsed_lang)
        analysis = reason_language(parsed_lang)
        print("[LANGUAGE PARSER] Reasoned:", analysis)
    else:
        print("[LANGUAGE PARSER] No valid language structure detected.")


if __name__ == "__main__":
    run_ocr_and_detect_intent()