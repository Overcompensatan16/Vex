import sys
import threading
import pytesseract
import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt
from cerebral_cortex.optic_nerve.vision_parser import infer_intent_from_text
from prefrontal_cortex.prefrontal_cortex.window_switcher import perform_window_switch


class VisionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Vision Intent Detector")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.info_label = QLabel("Press a button to perform an action")
        layout.addWidget(self.info_label)

        button_layout = QHBoxLayout()
        self.ocr_button = QPushButton("Scan Screen")
        self.ocr_button.clicked.connect(self.start_ocr_thread)
        button_layout.addWidget(self.ocr_button)

        self.cam_button = QPushButton("Toggle Camera Preview")
        self.cam_button.clicked.connect(self.toggle_camera_preview)
        button_layout.addWidget(self.cam_button)

        layout.addLayout(button_layout)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        self.setLayout(layout)

        self.camera_preview = False
        self.cam_thread = None

    def start_ocr_thread(self):
        thread = threading.Thread(target=self.ocr_and_switch)
        thread.start()

    def ocr_and_switch(self):
        self.update_status("[OCR] Starting screen parse...")
        screenshot = ImageGrab.grab()
        text = pytesseract.image_to_string(screenshot)
        self.update_status(f"[OCR] Detected text:\n{text.strip()}")

        intent = infer_intent_from_text(text)
        if intent:
            self.update_status(f"[ACTION] Intent matched: {intent['label']}")
            switch_to_window_by_keyword(intent)
        else:
            self.update_status("[ACTION] ℹ️ No switchable intent detected.")

    def toggle_camera_preview(self):
        if not self.camera_preview:
            self.camera_preview = True
            self.cam_button.setText("Stop Camera Preview")
            self.cam_thread = threading.Thread(target=self.run_camera)
            self.cam_thread.start()
        else:
            self.camera_preview = False
            self.cam_button.setText("Toggle Camera Preview")

    def run_camera(self):
        cap = cv2.VideoCapture(0)
        while self.camera_preview and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Camera Preview", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def update_status(self, message):
        self.result_box.append(message)


def main():
    app = QApplication(sys.argv)
    window = VisionApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
