#!/usr/bin/env python

import asyncio
import base64
import json
import time
import uuid
import websockets

stream_sid = None

def log(msg):
    print(msg)

def receive_media(message):
    global stream_sid
    media = message["media"]
    chunk = base64.b64decode(media["payload"])
    # testing
    now = time.time()
    filename = f"chunk{stream_sid}{now}"
    with open(filename, "ab") as f:
        f.write(chunk)

def payload_to_message(payload):
    global stream_sid
    return {"event": "media",
            "streamSid": stream_sid,
            "media": {"payload": payload}}

def mark_message():
    """Return a mark message which can be sent to the Twilio websocket."""
    global stream_sid
    return {"event": "mark",
            "streamSid": stream_sid,
            "mark": {"name": uuid.uuid4().hex}}

async def handle(websocket):
    """
    Handle every message in websocket until we receive a stop message or barf.
    """
    global stream_sid
    async for message in websocket:
        message = json.loads(message)
        if message["event"] == "connected":
            log(f"Received event 'connected': {message}")
        elif message["event"] == "start":
            log(f"Received event 'start': {message}")
            if stream_sid and stream_sid != message['streamSid']:
                raise Exception("Unexpected new streamSid")
            stream_sid = message['streamSid']
        elif message["event"] == "media":
            log("Received event 'media'")
            # This assumes we get messages in order, we should instead
            # verify the sequence numbers. message["sequenceNumber"]
            receive_media(message)
            # Send media back, for testing.
            await websocket.send(
                json.dumps(
                    payload_to_message(message["media"]["payload"])))
            # Send mark message, for testing. We should receive this back.
            await websocket.send(json.dumps(mark_message()))
        elif message["event"] == "stop":
            log(f"Received event 'stop': {message}")
            stream_sid = None
            break
        else:
            log(f"Received unexpected event: {message}")
    log("Connection closed")

async def main():
    async with websockets.serve(handle, "localhost", 6000):
        await asyncio.Future()  # run forever

asyncio.run(main())
