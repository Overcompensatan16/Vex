# cerebral_cortex/optic_nerve/vision_parser.py
"""
Capture a screenshot, run a robust OCR-preprocessing pipeline, extract
text with Tesseract, feed the combined text into Temporal-Lobe
`parse_language`, and package everything into a SymbolicSignal.
"""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image
import mss
import pytesseract
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
import uuid
from typing import Dict, List, Optional

from symbolic_signal import SymbolicSignal
from cerebral_cortex.temporal_lobe.language_parser import parse_language

# Point Tesseract to the local installation
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\Administrator\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)


# ────────────────────────── CAPTURE & PREPROCESS ────────────────────────── #
def capture_screen(region: Optional[Dict] = None) -> np.ndarray:
    """
    Returns a screenshot as an RGB NumPy array.
    `region` can be {'top','left','width','height'} to crop.
    """
    with mss.mss() as sct:
        monitor = region if region else sct.monitors[1]
        shot = sct.grab(monitor)
        pil_img = Image.frombytes("RGB", shot.size, shot.rgb)
        return np.array(pil_img)


def preprocess_image(img: np.ndarray) -> np.ndarray:
    """
    Grayscale → adaptive threshold → denoise → sharpen → resize → deskew
    for maximum OCR clarity.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    denoised = cv2.fastNlMeansDenoising(thresh, h=30)

    sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(denoised, -1, sharpen_kernel)

    resized = cv2.resize(sharpened, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

    coords = np.column_stack(np.where(resized > 0))
    if coords.size:
        angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + angle) if angle < -45 else -angle
        h, w = resized.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        deskewed = cv2.warpAffine(
            resized, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return deskewed
    return resized


# ───────────────────────────── MAIN PARSER ──────────────────────────────── #
def parse_screen(
    confidence_threshold: float = 60.0,
    region: Optional[Dict] = None,
) -> SymbolicSignal:
    """
    Capture → OCR → lightweight language parse → SymbolicSignal
    """
    img = capture_screen(region)
    proc_img = preprocess_image(img)

    ocr = pytesseract.image_to_data(proc_img, output_type=pytesseract.Output.DICT)

    text_blocks: List[Dict] = []
    for i in range(len(ocr["text"])):
        text = (ocr["text"][i] or "").strip()
        try:
            conf = float(ocr["conf"][i])
        except (ValueError, TypeError):
            conf = 0.0
        if text and conf >= confidence_threshold:
            text_blocks.append(
                {
                    "text": text,
                    "left": int(ocr["left"][i]),
                    "top": int(ocr["top"][i]),
                    "width": int(ocr["width"][i]),
                    "height": int(ocr["height"][i]),
                    "conf": conf,
                }
            )

    visible_files = [b["text"] for b in text_blocks if b["text"].endswith(".py")]

    combined = " ".join(b["text"] for b in text_blocks)
    parsed_text = parse_language(combined)

    data = {
        "raw_text_blocks": text_blocks,
        "visible_files": visible_files,
        "parsed_text": parsed_text,  # tokens + word_count
        "targets": {},
    }

    signal = SymbolicSignal(
        data=data,
        modality="vision",
        source="optic_nerve",
        tags=["ocr"],
    )
    signal.timestamp = datetime.now(ZoneInfo("America/Indiana/Indianapolis")).isoformat()
    return signal


# ─────────── Keyword-store helpers (unchanged) ─────────── #
def load_keyword_store() -> List[Dict]:
    path = os.path.join(os.path.dirname(__file__), "keyword_store.jsonl")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def generate_keyword_entry(text: str) -> Dict:
    return {
        "label": f"auto_{uuid.uuid4().hex[:8]}",
        "keywords": [text.strip()],
        "actions": [{"type": "tag", "target": "unknown"}],
        "context": ["auto_generated"],
        "priority": 6.1,
        "added_by": "autogen",
    }

