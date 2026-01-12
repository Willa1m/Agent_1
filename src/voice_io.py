from typing import Optional


class VoiceIOUnavailableError(RuntimeError):
    pass


class VoiceIO:
    def __init__(self) -> None:
        try:
            import speech_recognition as sr  # type: ignore
            import pyttsx3  # type: ignore
        except ImportError as exc:
            raise VoiceIOUnavailableError(
                "Voice IO dependencies are not installed. "
                "Install speechrecognition, pyaudio, and pyttsx3 to enable voice mode."
            ) from exc
        self._sr = sr
        self._recognizer = sr.Recognizer()
        self._tts_engine = pyttsx3.init()

    def listen(self, timeout: Optional[float] = None) -> str:
        with self._sr.Microphone() as source:
            audio = self._recognizer.listen(source, timeout=timeout)
        return self._recognizer.recognize_google(audio, language="zh-CN")

    def speak(self, text: str) -> None:
        self._tts_engine.say(text)
        self._tts_engine.runAndWait()


