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
    # XXX websocket_server.add_request
    util.log("speaker callback")

async def websocket_server_to_transcriber(websocket_server, transcriber):
    async for chunk in websocket_server.receive_media():
        transcriber.add_request(chunk)

async def transcriber_to_speaker(transcriber, speaker):
    async for string in transcriber.receive_transcriptions():
        speaker.add_request(string)

async def main():
    websocket_server = websocketserver.Server()
    transcriber = transcription.SpeechClientBridge(
        transcription.streaming_config)
    speaker = texttospeech.Client(speaker_callback)

    speaker_task = asyncio.create_task(speaker.start())

    transcriber_to_speaker_task = asyncio.create_task(
        transcriber_to_speaker(transcriber, speaker))
    transcriber_task = asyncio.create_task(transcriber.start())

    websocket_server_to_transcriber_task = asyncio.create_task(
        websocket_server_to_transcriber(websocket_server, transcriber))
    websocket_server_task = asyncio.create_task(websocket_server.start())

    # We should gather these if we want to be able to shut down or cancel.
    await websocket_server_task
    await websocket_server_to_transcriber_task
    await transcriber_to_speaker_task
    await speaker_task

asyncio.run(main())
