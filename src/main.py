import asyncio
import argparse
import sys
import time
from google import genai
from tenacity import RetryError

from config import load_gemini_settings
from conversation import GeminiChatClient
from logging_utils import configure_logging
from voice_io import VoiceIO, VoiceIOUnavailableError
from live_session import GeminiLiveSession


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent1-cli",
        description="Gemini 2.0 powered CLI assistant.",
    )
    parser.add_argument(
        "--mode",
        choices=["text", "voice", "live"],
        default="text",
        help="Interaction mode: text, voice, or live (Gemini Live).",
    )
    parser.add_argument(
        "--system-prompt-path",
        type=str,
        default="config/system_prompt.txt",
        help="Path to system prompt template.",
    )
    return parser


def run_text_chat(chat_client: GeminiChatClient) -> None:
    logger = configure_logging(name="agent1.cli.text")
    logger.info("Starting text chat. Type 'exit' or 'quit' to stop.")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            logger.info("Session terminated by user.")
            break
        if user_input.lower() in {"exit", "quit"}:
            logger.info("Exiting chat session.")
            break
        if not user_input:
            continue
        try:
            reply = chat_client.send_message(user_input)
            time.sleep(1)  # Basic rate limiting
        except RetryError:
            logger.error("API quota exceeded after retries. Please wait a moment and try again.")
            continue
        except Exception as exc:
            logger.error("Error while calling Gemini API: %s", exc)
            continue
        print(f"AI: {reply}")


def run_voice_chat(chat_client: GeminiChatClient) -> None:
    logger = configure_logging(name="agent1.cli.voice")
    try:
        voice = VoiceIO()
    except VoiceIOUnavailableError as exc:
        logger.error(str(exc))
        return
    logger.info("Starting voice chat. Press Ctrl+C to stop.")
    try:
        while True:
            logger.info("Listening...")
            try:
                text = voice.listen()
            except Exception as exc:
                logger.error("Voice recognition error: %s", exc)
                continue
            if not text:
                continue
            logger.info("You said: %s", text)
            try:
                reply = chat_client.send_message(text)
            except Exception as exc:
                logger.error("Error while calling Gemini API: %s", exc)
                continue
            logger.info("AI reply: %s", reply)
            voice.speak(reply)
    except KeyboardInterrupt:
        logger.info("Voice session terminated by user.")


def run_live_chat(client: genai.Client, model: str, system_prompt: str | None) -> None:
    logger = configure_logging(name="agent1.cli.live")
    session = GeminiLiveSession(client, model, system_prompt)
    
    logger.info("Starting Gemini Live session. Press Ctrl+C to stop.")
    try:
        asyncio.run(session.start())
    except KeyboardInterrupt:
        logger.info("Live session terminated by user.")
        session.stop()
    except Exception as e:
        logger.error(f"Live session error: {e}")
        session.stop()


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        settings = load_gemini_settings(default_prompt_path=args.system_prompt_path)
    except RuntimeError as e:
        print(f"Configuration Error: {e}")
        return 1

    client = genai.Client(api_key=settings.api_key, http_options={"api_version": "v1alpha"})

    print(f"DEBUG: Active Model -> {settings.model}")
    print(f"DEBUG: Interaction Mode -> {args.mode}")

    if args.mode == "live":
        run_live_chat(client, settings.model, settings.system_prompt)
    else:
        chat_client = GeminiChatClient(
            client=client,
            model=settings.model,
            system_prompt=settings.system_prompt,
        )
        if args.mode == "voice":
            run_voice_chat(chat_client)
        else:
            run_text_chat(chat_client)

    return 0


if __name__ == "__main__":
    sys.exit(main())
