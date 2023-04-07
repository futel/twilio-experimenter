import asyncio
import glob

import transcription

async def foo():
    bridge = transcription.SpeechClientBridge(
        transcription.streaming_config,
        transcription.on_transcription_response)
    start_future = bridge.start()

    for filename in sorted(glob.glob("misc/chunks/*")): #[0:20]:
        with open(filename, "rb") as chunk:
            print("xxx chunk")
            chunk = chunk.read()
            #chunk = base64.b64decode(chunk)
            bridge.add_request(chunk)
            #await asyncio.sleep(0.1)

    print("xxx bar")
    #await asyncio.sleep(10)
    #print("xxx baz")
    await start_future
    #bridge.terminate()

if __name__ == "__main__":
    asyncio.run(foo())
