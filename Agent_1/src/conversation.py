import logging
from collections import deque
from typing import Deque, Iterable, List, Optional

from google import genai
from google.genai import types
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


def is_retryable_error(exception: BaseException) -> bool:
    """Check if the exception is a retryable API error (e.g., 429)."""
    msg = str(exception)
    return "429" in msg or "RESOURCE_EXHAUSTED" in msg or "Too Many Requests" in msg


class ChatHistory:
    def __init__(self, max_turns: int = 20) -> None:
        self._messages: Deque[types.Content] = deque(maxlen=max_turns * 2)

    @property
    def messages(self) -> List[types.Content]:
        return list(self._messages)

    def add_user_message(self, text: str) -> None:
        self._messages.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=text)],
            )
        )

    def add_model_message(self, text: str) -> None:
        self._messages.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=text)],
            )
        )


class GeminiChatClient:
    def __init__(
        self,
        client: genai.Client,
        model: str,
        system_prompt: Optional[str] = None,
        max_turns: int = 20,
    ) -> None:
        self._client = client
        self._model = model
        self._history = ChatHistory(max_turns=max_turns)
        self._config: Optional[types.GenerateContentConfig] = None
        if system_prompt:
            self._config = types.GenerateContentConfig(
                system_instruction=system_prompt
            )

    @property
    def history(self) -> Iterable[types.Content]:
        return self._history.messages

    @retry(
        retry=retry_if_exception(is_retryable_error),
        wait=wait_exponential(multiplier=2, min=10, max=120),
        stop=stop_after_attempt(10),
        before_sleep=before_sleep_log(logger, logging.INFO),
    )
    def send_message(self, text: str) -> str:
        self._history.add_user_message(text)
        contents = list(self._history.messages)
        
        # Ensure system instruction is passed correctly to generate_content
        # For google-genai SDK, it might be better to pass it in the config object
        
        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=self._config,
        )
        output_text = response.text or ""
        self._history.add_model_message(output_text)
        return output_text


