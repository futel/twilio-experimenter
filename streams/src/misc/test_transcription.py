import asyncio
import glob

import transcription

async def get_chunks():
    for filename in sorted(glob.glob("misc/chunks/*")):
        with open(filename, "rb") as chunk:
            print("xxx chunk")
            chunk = chunk.read()
            #chunk = base64.b64decode(chunk)
            yield chunk
            await asyncio.sleep(0.1)

def callback(response):
    print(response)

async def foo():
    bridge = transcription.SpeechClientBridge(transcription.streaming_config, callback=callback)

    bridge_task = asyncio.create_task(bridge.start())

    async for chunk in get_chunks():
        bridge.add_request(chunk)

    await bridge_task
    #bridge.terminate()

if __name__ == "__main__":
    asyncio.run(foo())
