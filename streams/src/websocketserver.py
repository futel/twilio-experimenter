#!/usr/bin/env python

import asyncio
import websockets

def log(msg):
    print(msg)

async def echo(websocket):
    async for message in websocket:
        log(message)
        await websocket.send(message)

async def main():
    async with websockets.serve(echo, "localhost", 6000):
        await asyncio.Future()  # run forever

asyncio.run(main())
