import asyncio
from google.cloud import speech_v1

import util

# alternatives {
#   transcript: " Donald Duck"
# }
# stability: 0.8999999761581421
# result_end_time {
#   seconds: 15
#   nanos: 950000000
# }
# language_code: "en-us"

# alternatives {
#   transcript: " Donald Duck"
#   confidence: 0.6944478750228882
# }
# is_final: true
# result_end_time {
#   seconds: 16
#   nanos: 10000000
# }
# language_code: "en-us"


# XXX this gets creds from env?
# XXX set for cheaper rate by letting google record
# adaptation?
# speech_contexts?
# enable_automatic_punctuation=True
# model latest_long phone_call
# use_enhanced=True
# max_alternatives
config = speech_v1.RecognitionConfig(
    encoding=speech_v1.RecognitionConfig.AudioEncoding.MULAW,
    sample_rate_hertz=8000,
    language_code="en-US")
streaming_config = speech_v1.StreamingRecognitionConfig(
    config=config,
    interim_results=True)


class SpeechClientBridge:
    """
    Class to process and emit transcription.
    Calls callback with responses.
    Call start() to begin. Call terminate() to end.
    Call add_request() to add chunks.
    """
    def __init__(self, streaming_config, callback):
        self._queue = asyncio.Queue()
        self._ended = False
        self._callback = callback
        self.streaming_config = streaming_config
        self.client = speech_v1.SpeechAsyncClient()

    async def start(self):
        """
        Process our requests and yield the responses until we are terminated.
        """
        responses = await self.client.streaming_recognize(requests=self.request_generator())
        async for response in responses:
            await self.on_transcription_response(response)
            if self._ended:
                break

    def terminate(self):
        """Stop the request and response processing."""
        self._ended = True

    def add_request(self, buffer):
        """Add a chunk of bytes, or None, to the processing queue."""
        if buffer is not None:
            buffer = bytes(buffer)
        self._queue.put_nowait(buffer)

    async def request_generator(self):
        """
        Yield streaming recognize requests. The first contains the config, the remainder contain
        audio.
        """
        yield speech_v1.StreamingRecognizeRequest(streaming_config=self.streaming_config)
        async for content in self.audio_generator():
            yield speech_v1.StreamingRecognizeRequest(audio_content=content)

    async def audio_generator(self):
        """
        Get concatenate, and yield all the bytes in the queue
        until it is empty or contains a None.
        """
        while not self._ended:
            # Await get() to ensure there's at least one chunk
            # of data, and stop iteration if the chunk is None,
            # which was put in there to indicate the end of the audio stream.
            # XXX will not notice _ended while waiting
            chunk = await self._queue.get()
            if chunk is None:
                return
            data = [chunk]

            # Consume all buffered data.
            while True:
                try:
                    chunk = self._queue.get_nowait()
                    if chunk is None:
                        # XXX we throw away what we have?
                        return
                    data.append(chunk)
                except asyncio.QueueEmpty:
                    break

            yield b"".join(data)

    async def on_transcription_response(self, response):
        if not response.results:
            util.log("no results")
            return
        try:
            is_final = response.results[0].is_final
        except AttributeError:
            is_final = False
        if not is_final:
            util.log("not final")
            return None
        result = response.results[0]
        if not result.alternatives:
            util.log("no alternatives")
            return
        util.log("final")
        await self._callback(result.alternatives[0].transcript)
