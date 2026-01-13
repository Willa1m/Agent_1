import asyncio
import pyaudio
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
        self.output_queue = asyncio.Queue()
        self.play_task = None
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
        self.play_task = asyncio.create_task(self._play_loop())
        logger.info("Speaker output started")

    async def _play_loop(self):
        loop = asyncio.get_running_loop()
        while self.running:
            try:
                data = await self.output_queue.get()
                if self.output_stream and self.output_stream.is_active():
                    # Run blocking write in executor to avoid blocking the loop
                    await loop.run_in_executor(None, self.output_stream.write, data)
                self.output_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Playback error: {e}")

    async def get_audio_chunk(self):
        return await self.input_queue.get()

    def play_audio_chunk(self, data):
        try:
            self.output_queue.put_nowait(data)
        except asyncio.QueueFull:
            pass

    def clear_output(self):
        """Clear pending audio to stop playback immediately (Barge-in)."""
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
                self.output_queue.task_done()
            except asyncio.QueueEmpty:
                break
        logger.info("Audio output cleared")

    def stop(self):
        self.running = False
        if self.play_task:
            self.play_task.cancel()
            
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        self.p.terminate()
        logger.info("Audio streams stopped")
