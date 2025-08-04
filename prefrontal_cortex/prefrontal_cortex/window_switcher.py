import pygetwindow as gw
import pyautogui
from datetime import datetime, timezone


def perform_window_switch(matched_window: dict) -> dict:
    """
    Attempts to switch focus to a window based on the matched_window dictionary from window_intent_gate.
    Returns a structured dict with result, timestamp, and bounding box info.
    """
    try:
        window_title = matched_window.get("title")
        requires_toggle = matched_window.get("requires_toggle", False)

        if requires_toggle:
            # Toggle-based switching logic for special apps (e.g., Discord)
            try:
                pyautogui.hotkey("ctrl", "alt", "d")  # Example toggle combo
                return {
                    "status": "success",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "window_title": window_title,
                    "bounding_box": matched_window["bounding_box"],
                    "method": "hotkey_toggle"
                }
            except Exception as e:
                return {
                    "status": "fail",
                    "error": f"Toggle hotkey failed: {str(e)}",
                    "attempted_title": window_title,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

        for win in gw.getWindowsWithTitle(window_title):
            if win.title == window_title:
                win.activate()
                pyautogui.moveTo(win.left + 10, win.top + 10)  # Light focus click if needed
                pyautogui.click()

                return {
                    "status": "success",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "window_title": win.title,
                    "bounding_box": {
                        "left": win.left,
                        "top": win.top,
                        "width": win.width,
                        "height": win.height
                    },
                    "method": "title_match"
                }

        return {
            "status": "fail",
            "error": "Window title not found.",
            "attempted_title": window_title,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        return {
            "status": "fail",
            "error": str(e),
            "attempted_title": matched_window.get("title", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
