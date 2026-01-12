import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
GEMINI_MODEL_ENV = "GEMINI_MODEL"
SYSTEM_PROMPT_PATH_ENV = "SYSTEM_PROMPT_PATH"


@dataclass
class GeminiSettings:
    api_key: str
    model: str
    system_prompt: str | None


def load_system_prompt(default_path: str | None = None) -> str | None:
    prompt_path = os.environ.get(SYSTEM_PROMPT_PATH_ENV) or default_path
    if not prompt_path:
        return None
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip() or None
    except FileNotFoundError:
        return None


def load_gemini_settings(
    default_model: str = "gemini-2.5-flash",
    default_prompt_path: str | None = None,
) -> GeminiSettings:
    api_key = os.environ.get(GEMINI_API_KEY_ENV, "").strip()
    if not api_key:
        raise RuntimeError(
            f"Environment variable {GEMINI_API_KEY_ENV} must be set for Gemini access."
        )
    model = os.environ.get(GEMINI_MODEL_ENV, default_model).strip() or default_model
    system_prompt = load_system_prompt(default_prompt_path)
    return GeminiSettings(api_key=api_key, model=model, system_prompt=system_prompt)


