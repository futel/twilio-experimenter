#!/usr/bin/env python

import asyncio
import functools
#import time

import transcription
import util
import websocketserver

# def save_chunk(chunk):
#     # testing
#     now = time.time()
#     filename = f"chunk{stream_sid}{now}"
#     with open(filename, "ab") as f:
#         f.write(chunk)

def transcription_callback(response):
    util.log(response)

async def main():
    transcriber = transcription.SpeechClientBridge(
        transcription.streaming_config, callback=transcription_callback)
    transcriber_task = asyncio.create_task(transcriber.start())

    def send_callback():
        return asyncio.Future()

    websocket_server = websocketserver.Server(
        recv_media_callback=transcriber.add_request,
        send_callback=send_callback)
    websocketserver_task = asyncio.create_task(websocket_server.start())

    # We should gather these if we want to be able to shut down or cancel.
    await websocketserver_task
    await transcriber_task

asyncio.run(main())
