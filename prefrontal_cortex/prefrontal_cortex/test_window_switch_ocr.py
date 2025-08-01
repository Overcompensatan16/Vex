import time
import json
import pytesseract
import pyautogui
import pygetwindow as gw
from PIL import ImageGrab

from basal_ganglia.window_intent_gate import gate_window_switch
from prefrontal_cortex.prefrontal_cortex.window_switcher import perform_window_switch

# === OCR CONFIG ===
tess_path = r"C:\\Users\\Administrator\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = tess_path


def capture_screen_region(region=None):
    """Capture full screen or defined region and return PIL image"""
    img = ImageGrab.grab(bbox=region)
    return img


def extract_text_from_image(image):
    """Run OCR on image and return detected text"""
    return pytesseract.image_to_string(image)


def infer_intent_from_text(text):
    """Simple keyword scanner to produce a window switch intent"""
    lowered = text.lower()
    if "discord" in lowered:
        return {"intent": "switch_to", "target_label": "discord"}
    elif "opera" in lowered or "browser" in lowered:
        return {"intent": "switch_to", "target_label": "opera_gx"}
    return None


def test_switch_pipeline():
    print("[TEST] Capturing screen...")
    screen = capture_screen_region()
    text = extract_text_from_image(screen)

    print("[TEST] OCR Result:\n", text)
    intent = infer_intent_from_text(text)

    if not intent:
        print("[TEST] ❌ No matching intent found in screen text.")
        return

    print(f"[TEST] Detected intent: {intent}")
    result = gate_window_switch(intent)

    if result["status"] != "approved":
        print("[TEST] ❌ Switch inhibited: No matching window.")
        return

    print(f"[TEST] ✅ Approved switch target: {result['matched_window']['label']}")
    switch_result = perform_window_switch(result["matched_window"])

    if switch_result["status"] == "success":
        print(f"[TEST] 🎉 Switched to {switch_result['window_title']} using {switch_result['method']}")
    else:
        print(f"[TEST] ❌ Switch failed: {switch_result['error']}")


if __name__ == "__main__":
    print("\n=== OCR → INTENT → SWITCH TEST HARNESS ===")
    test_switch_pipeline()
    time.sleep(1)
