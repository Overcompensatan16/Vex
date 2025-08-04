import time
import pygetwindow as gw
import pyautogui
from cerebral_cortex.optic_nerve.vision_parser import parse_screen
from cerebral_cortex.optic_nerve.vision_reasoner import reason_screen  # ✅ Import vision reasoner


def get_best_window(target_keywords):
    """
    Scans open windows for one matching target_keywords in title.
    Returns bounding box of best match.
    """
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
            "height": best_match.height,
            "title": best_match.title
        }
    else:
        return None


def map_and_parse_screen(target_keywords):
    region = get_best_window(target_keywords)
    if not region:
        return {"error": "No matching window found."}

    print(f"[ScreenMapper] Focusing window: {region['title']}")
    pyautogui.click(region["left"] + 10, region["top"] + 10)  # Focus click
    time.sleep(0.2)  # Let it update

    bounding_box = {
        "top": region["top"],
        "left": region["left"],
        "width": region["width"],
        "height": region["height"]
    }
    return parse_screen(region=bounding_box)


if __name__ == "__main__":
    keywords = ["notepad", "calc", "visual studio", "vscode"]
    signal = map_and_parse_screen(keywords)
    parsed = signal.data if hasattr(signal, "data") else signal

    if parsed is None or "error" in parsed:
        raise RuntimeError("No matching window found to parse.")
    else:
        print("--- PARSED DATA ---")

        symbolic = reason_screen(parsed)  # ✅ Add reasoning pass
        for block in symbolic.get("raw_text_blocks", []):
            print(block)
