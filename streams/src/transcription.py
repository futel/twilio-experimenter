import base64
import glob
import queue
import threading
import time

from google.cloud import speech

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
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.MULAW,
    sample_rate_hertz=8000,
    language_code="en-US")
streaming_config = speech.StreamingRecognitionConfig(
    config=config, interim_results=True)

def log(msg):
    print(msg)

def on_transcription_response(response):
    if not response.results:
        log("no results")
        return
    result = response.results[0]
    if not result.alternatives:
        log("no alternatives")
        return
    transcription = result.alternatives[0].transcript
    #log("Transcription: " + transcription)
    log("Transcription: " + str(result))


class SpeechClientBridge:
    """
    Class to process and emit transcription.
    Calls on_response with responses.
    Call start() to begin. Call terminate() to end. Note that start()
    does not return, we will need a thread.
    Call add_request() to add chunks.
    """
    def __init__(self, streaming_config, on_response):
        self._on_response = on_response
        self._queue = queue.Queue()
        self._ended = False
        self.streaming_config = streaming_config

    def start(self):
        """
        Set up generators to process requests and responses from
        the transcription service until we are terminated.
        """
        client = speech.SpeechClient()
        stream = self.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in stream)
        responses = client.streaming_recognize(
            self.streaming_config, requests)
        self.process_responses_loop(responses)

    def terminate(self):
        """Stop the request and response processing."""
        self._ended = True

    def add_request(self, buffer):
        """Add a chunk of bytes, or None, to the processing queue."""
        if buffer is not None:
            buffer = bytes(buffer)
        self._queue.put(buffer, block=False)

    def process_responses_loop(self, responses):
        """Process the responses generator until we are terminated."""
        for response in responses:
            self._on_response(response)

            if self._ended:
                break

    def generator(self):
        """
        Get and yield all the bytes in the queue until it contains a None.
        """
        while not self._ended:
            # Use a blocking get() to ensure there's at least one chunk
            # of data, and stop iteration if the chunk is None,
            # indicating the end of the audio stream.
            chunk = self._queue.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._queue.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

if __name__ == "__main__":
    # XXX testing
    bridge = SpeechClientBridge(
        streaming_config, on_transcription_response)
    # Start the bridge in a thread, since the start method doesn't
    # return until the bridge is terminated.
    # XXX the websocketserver is async and we should be too
    t = threading.Thread(target=bridge.start)
    t.start()

    for filename in sorted(glob.glob("test/chunks/*")):
       with open(filename, "rb") as chunk:
           chunk = chunk.read()
           #chunk = base64.b64decode(chunk)
           bridge.add_request(chunk)

    # XXX instead, wait for bridge to be done or whatever
    log("sleeping")
    time.sleep(10)

    bridge.add_request(None)
    bridge.terminate()
