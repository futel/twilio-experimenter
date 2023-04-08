#!/usr/bin/env python

import asyncio
import functools
#import time

import texttospeech
import transcription
import util
import websocketserver

# def save_chunk(chunk):
#     # testing
#     now = time.time()
#     filename = f"chunk{stream_sid}{now}"
#     with open(filename, "ab") as f:
#         f.write(chunk)

def speaker_callback(response):
    util.log("speaker callback")

async def main():

    speaker = texttospeech.Client(speaker_callback)

    transcriber = transcription.SpeechClientBridge(
        transcription.streaming_config, callback=speaker.add_request)
    transcriber_task = asyncio.create_task(transcriber.start())

    websocket_server = websocketserver.Server(
        recv_media_callback=transcriber.add_request)
    websocketserver_task = asyncio.create_task(websocket_server.start())

    # We should gather these if we want to be able to shut down or cancel.
    await websocketserver_task
    await transcriber_task

asyncio.run(main())
