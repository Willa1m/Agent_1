import asyncio
import logging
import os
import traceback
from google import genai
from live_audio import AudioStream

logger = logging.getLogger(__name__)

class GeminiLiveSession:
    def __init__(self, client: genai.Client, model: str, system_prompt: str | None = None):
        self.client = client
        self.model = model
        self.system_prompt = system_prompt
        self.audio_stream = AudioStream()
        self.session = None

    async def start(self):
        self.audio_stream.start_input()
        self.audio_stream.start_output()
        
        # Use the BidiGenerateContent API for real-time streaming
        config = {"response_modalities": ["AUDIO"]}
        if self.system_prompt:
             config["system_instruction"] = self.system_prompt

        logger.info(f"Connecting to Gemini Live ({self.model})...")
        
        async with self.client.aio.live.connect(model=self.model, config=config) as session:
            self.session = session
            logger.info("Connected! Start speaking...")
            
            # Run send and receive loops concurrently
            await asyncio.gather(
                self._send_audio_loop(),
                self._receive_loop()
            )

    async def _send_audio_loop(self):
        try:
            while True:
                chunk = await self.audio_stream.get_audio_chunk()
                if chunk:
                     await self.session.send(input={"data": chunk, "mime_type": "audio/pcm"}, end_of_turn=False)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error sending audio: {e}")

    async def _receive_loop(self):
        try:
            async for response in self.session.receive():
                if response.server_content is None:
                    continue

                if getattr(response.server_content, "interrupted", False):
                    logger.info("Interrupted by user input.")
                    self.audio_stream.clear_output()
                    continue

                model_turn = response.server_content.model_turn
                if model_turn is not None:
                    for part in model_turn.parts:
                        if part.inline_data is not None:
                             # Play received audio chunk
                             self.audio_stream.play_audio_chunk(part.inline_data.data)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error receiving audio: {e}")
            traceback.print_exc()

    def stop(self):
        self.audio_stream.stop()
