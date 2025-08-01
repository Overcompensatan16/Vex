import os
import wave
import pyaudio
import json
import threading
import speech_recognition as sr
from datetime import datetime, UTC, timezone
from audit.audit_logger_factory import AuditLoggerFactory
from cerebral_cortex.temporal_lobe.context_tracker import ContextTracker


# === Audio Storage Config === #
AUDIO_DIR = os.path.join(os.path.expanduser("~"), "Music", "VexAudio")
LOG_PATH = os.path.join(AUDIO_DIR, "ear_audio_log.jsonl")
RECORD_SECONDS = 5
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2
CHUNK = 1024

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


def get_filename():
    """Generate a unique filename for audio recordings based on timestamp."""
    timestamp_obj = datetime.now(UTC)
    timestamp = timestamp_obj.isoformat().replace(":", "-")
    name = f"audio_{timestamp}.wav"
    return os.path.join(AUDIO_DIR, name), timestamp_obj.isoformat()


def record_audio(seconds=RECORD_SECONDS):
    """Record raw audio data from the default microphone."""
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pa.get_format_from_width(SAMPLE_WIDTH),
                     channels=CHANNELS,
                     rate=SAMPLE_RATE,
                     input=True,
                     frames_per_buffer=CHUNK)

    print(f"[EarModule] Recording {seconds} seconds...")
    frames = []
    for _ in range(0, int(SAMPLE_RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    pa.terminate()
    return b"".join(frames)


def save_wav(path, data):
    """Save audio bytes as a .wav file."""
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(data)


class EarModule:
    """Vex EarModule: microphone + internal audio STT + symbolic auditing."""

    def __init__(self, audit_log_path=None, context_size: int = 10):
        self.logger = AuditLoggerFactory.get_logger("ear")
        self.context = ContextTracker(max_size=context_size)
        self.recognizer = sr.Recognizer()
        self._mic = self._init_mic()
        self._listening_thread = None
        self._active = False
        print("[EarModule] Initialized.")

    @staticmethod
    def _init_mic():
        try:
            mic = sr.Microphone()
            print("[EarModule] Microphone available.")
            return mic
        except Exception as e:
            print(f"[EarModule] Mic unavailable: {e}")
            return None

    def capture_from_mic(self, timeout=5, phrase_time_limit=10):
        """Capture, store, and transcribe voice from live mic input."""
        if not self._mic:
            return self._fail("mic_unavailable")

        path, timestamp = get_filename()
        audio_bytes = record_audio()
        save_wav(path, audio_bytes)

        try:
            with sr.AudioFile(path) as source:
                audio = self.recognizer.record(source)
                transcript = self.recognizer.recognize_google(audio)
                return self._log_event(transcript, "mic", path)
        except Exception as e:
            return self._fail("mic_transcription_error", str(e))

    def capture_loopback(self, audio_path):
        """Transcribe from an audio file (e.g. internal audio/loopback recording)."""
        try:
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
                transcript = self.recognizer.recognize_google(audio)
                return self._log_event(transcript, "loopback", audio_path)
        except Exception as e:
            return self._fail("loopback_error", str(e))

    def capture_from_text(self, text):
        """Simulate input for symbolic or scripted text."""
        return self._log_event(text, "text")

    def capture(self, source=None):
        """
        Unified capture helper.

        If ``source`` is ``None`` and a microphone is available, capture from the mic.
        If ``source`` is a path to an existing file, treat it as an audio file.
        Otherwise, ``source`` is assumed to be text.
        """
        if source is None:
            return self.capture_from_mic()
        if isinstance(source, str) and os.path.exists(source):
            return self.capture_loopback(source)
        return self.capture_from_text(str(source))

    def listen_forever(self, phrase_time_limit=6):
        """Begin passive STT monitoring from microphone in a background thread."""
        if not self._mic:
            print("[EarModule] Cannot listen in background: mic unavailable.")
            return

        def listen_loop():
            print("[EarModule] Background listening started.")
            self._active = True
            with self._mic as source:
                self.recognizer.adjust_for_ambient_noise(source)
                while self._active:
                    try:
                        audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=phrase_time_limit)
                        transcript = self.recognizer.recognize_google(audio)
                        self._log_event(transcript, "mic_background")
                    except Exception as e:
                        print(f"[EarModule] Background STT error: {e}")

        if not self._listening_thread or not self._listening_thread.is_alive():
            self._listening_thread = threading.Thread(target=listen_loop, daemon=True)
            self._listening_thread.start()

    def stop_listening(self):
        """Stop background listening."""
        self._active = False
        print("[EarModule] Background listening stopped.")

    def _log_event(self, transcript, mode, audio_path=None):
        """Store symbolic capture event."""
        event = {
            "captured": transcript.strip(),
            "mode": mode,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "ear_module",
            "audio_path": audio_path or "not_recorded"
        }
        self.logger.log_event("capture", event)
        self.context.add(event)
        return event

    def _fail(self, reason, error=None):
        """Standardized error signal."""
        print(f"[EarModule] {reason}: {error or 'Unknown error'}")
        event = {
            "captured": None,
            "error": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "ear_module",
        }
        self.logger.log_error(reason, str(error) if error else "")
        self.context.add(event)
        return event


__all__ = ["EarModule"]
