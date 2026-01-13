from typing import Optional


class VoiceIOUnavailableError(RuntimeError):
    pass


import time

class VoiceIO:
    def __init__(self) -> None:
        self._mock = False
        try:
            import speech_recognition as sr  # type: ignore
            import pyttsx3  # type: ignore
            self._sr = sr
            self._recognizer = sr.Recognizer()
            self._tts_engine = pyttsx3.init()
        except ImportError:
            print("WARNING: Voice IO dependencies missing. Using MOCK VoiceIO.")
            self._mock = True

    def listen(self, timeout: Optional[float] = None) -> str:
        if self._mock:
            # Simulate a delay and return mock text
            time.sleep(2)
            return "Hello Gemini, this is a test."

        with self._sr.Microphone() as source:
            audio = self._recognizer.listen(source, timeout=timeout)
        return self._recognizer.recognize_google(audio, language="zh-CN")

    def speak(self, text: str) -> None:
        if self._mock:
            print(f"[MOCK SPEAKER]: {text}")
            return

        self._tts_engine.say(text)
        self._tts_engine.runAndWait()


