import asyncio
from google.cloud import texttospeech_v1

import util

# XXX this gets creds from env?

class Client:
    """
    Class to process and emit speech.
    Calls callback with responses.
    Call add_request() to add text.
    """
    def __init__(self, callback):
        self.client = texttospeech_v1.TextToSpeechAsyncClient()
        self._voice = texttospeech_v1.VoiceSelectionParams()
        self._voice.language_code = "en-US"
        self._audio_config = texttospeech_v1.AudioConfig()
        self._audio_config.audio_encoding = "MULAW"
        self._callback = callback

    async def add_request(self, text):
        input_ = texttospeech_v1.SynthesisInput()
        input_.text = text

        request = texttospeech_v1.SynthesizeSpeechRequest(
            input=input_,
            voice=self._voice,
            audio_config=self._audio_config)

        response = await self.client.synthesize_speech(request=request)
        self._callback(response.audio_content)
