#!/usr/bin/env python

import asyncio
import functools
import time

import texttospeech
import transcription
import util
import websocketserver

# def save_chunk(chunk):
#     # testing
#     now = time.time()
#     filename = f"chunk{now}"
#     with open(filename, "ab") as f:
#         f.write(chunk)

async def websocket_to_transcriber(websocket_server, transcriber):
    async for chunk in websocket_server.receive_response():
        transcriber.add_request(chunk)

async def transcriber_to_speaker(transcriber, speaker):
    async for string in transcriber.receive_response():
        speaker.add_request(string)

async def speaker_to_websocket(speaker, websocket):
    async for chunk in speaker.receive_response():
        websocket.add_request(chunk)

async def main():
    speaker = texttospeech.Client()
    transcriber = transcription.SpeechClientBridge()
    websocket = websocketserver.Server()

    speaker_to_websocket_task = asyncio.create_task(
        speaker_to_websocket(speaker, websocket))
    speaker_task = asyncio.create_task(speaker.start())

    transcriber_to_speaker_task = asyncio.create_task(
        transcriber_to_speaker(transcriber, speaker))
    transcriber_task = asyncio.create_task(transcriber.start())

    websocket_to_transcriber_task = asyncio.create_task(
        websocket_to_transcriber(websocket, transcriber))
    websocket_task = asyncio.create_task(websocket.start())

    # We should gather these if we want to be able to shut down or cancel.
    await websocket_task
    await websocket_to_transcriber_task
    await transcriber_to_speaker_task
    await speaker_task
    await speaker_to_websocket_task

asyncio.run(main())
