#!/usr/bin/env python

import asyncio
import functools
import time

import speech
import transcription
import util
import websocketserver

# def save_chunk(chunk):
#     # testing
#     now = time.time()
#     filename = f"chunk{now}"
#     with open(filename, "ab") as f:
#         f.write(chunk)

def pipeline_tasks(producer, consumer):
    """Return tasks to start producer and send producer messages to consumer."""
    async def step_generator():
        """ Async generator to receive from producer and send to consumer."""
        async for item in producer.receive_response():
            consumer.add_request(item)
    start_task = asyncio.create_task(producer.start())
    step_task = asyncio.create_task(step_generator())
    return (start_task, step_task)

async def main():
    speaker = speech.Client()
    transcriber = transcription.SpeechClientBridge()
    websocket = websocketserver.Server()

    (speaker_to_websocket_task, speaker_task) = pipeline_tasks(speaker, websocket)
    (transcriber_to_speaker_task, transcriber_task) = pipeline_tasks(transcriber, speaker)
    (websocket_to_transcriber_task, websocket_task) = pipeline_tasks(websocket, transcriber)

    # We should gather these if we want to be able to shut down or cancel.
    await websocket_task
    await websocket_to_transcriber_task
    await transcriber_task
    await transcriber_to_speaker_task
    await speaker_task
    await speaker_to_websocket_task

asyncio.run(main())
