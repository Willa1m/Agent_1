import asyncio
import pyaudio
import queue
import logging

logger = logging.getLogger(__name__)

class AudioStream:
    def __init__(self, rate=16000, chunk_size=1024):
        self.rate = rate
        self.chunk_size = chunk_size
        self.p = pyaudio.PyAudio()
        self.input_stream = None
        self.output_stream = None
        self.input_queue = asyncio.Queue()
        self.running = False

    def start_input(self):
        def callback(in_data, frame_count, time_info, status):
            if self.running:
                try:
                    self.input_queue.put_nowait(in_data)
                except asyncio.QueueFull:
                    pass
            return (None, pyaudio.paContinue)

        self.input_stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=callback
        )
        self.input_stream.start_stream()
        self.running = True
        logger.info("Microphone input started")

    def start_output(self):
        self.output_stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk_size
        )
        logger.info("Speaker output started")

    async def get_audio_chunk(self):
        return await self.input_queue.get()

    def play_audio_chunk(self, data):
        if self.output_stream and self.output_stream.is_active():
            self.output_stream.write(data)

    def stop(self):
        self.running = False
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        self.p.terminate()
        logger.info("Audio streams stopped")
