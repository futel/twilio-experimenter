import asyncio

import texttospeech

def callback(out):
    with open("out.wav", 'wb') as f:
        f.write(out)
    print("callback")

async def foo():
    client = texttospeech.Client(callback)
    await client.add_request("testing one two threee")

if __name__ == "__main__":
    asyncio.run(foo())
