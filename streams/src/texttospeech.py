import asyncio
from google.cloud import texttospeech_v1

import util

# XXX this gets creds from env?

voice = texttospeech_v1.VoiceSelectionParams()
voice.language_code = "en-US"
audio_config = texttospeech_v1.AudioConfig()
audio_config.audio_encoding = "MULAW"
audio_config.sample_rate_hertz = 8000

class Client:
    """
    Class to process and emit speech.
    Calls callback with responses.
    Call add_request() to add text.
    """
    def __init__(self):
        self._send_queue = asyncio.Queue()
        self._recv_queue = asyncio.Queue()
        self._client = texttospeech_v1.TextToSpeechAsyncClient()

    async def start(self):
        """
        Process our requests and enqueue chunk response.
        """
        util.log("text to speech client starting")
        async for request in self.request_generator():
            response = await self._client.synthesize_speech(request=request)
            chunk = util.wav_to_chunk(response.audio_content)
            self._recv_queue.put_nowait(chunk)

    async def receive_response(self):
        """Generator for received media chunks."""
        # XXX need to stop when there won't be any more
        while True:
            yield await self._recv_queue.get()

    def add_request(self, text):
        """Add text to the processing queue."""
        self._send_queue.put_nowait(text)

    async def request_generator(self):
        while True:
            text = await self._send_queue.get()
            util.log(f"texttospeech request: {text}")
            input_ = texttospeech_v1.SynthesisInput()
            input_.text = text
            yield texttospeech_v1.SynthesizeSpeechRequest(
                input=input_,
                voice=voice,
                audio_config=audio_config)
