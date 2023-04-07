#!/usr/bin/env python

import asyncio
import base64
import json
import time
import uuid
import websockets

import transcription
import util

host = "localhost"
port = 6000

class Server:

    def __init__(self):
        self.stream_sid = None

    def receive_media(self, message):
        media = message["media"]
        chunk = base64.b64decode(media["payload"])

    # def payload_to_message(payload):
    #     return {"event": "media",
    #             "streamSid": self.stream_sid,
    #             "media": {"payload": payload}}

    def mark_message(self):
        """Return a mark message which can be sent to the Twilio websocket."""
        return {"event": "mark",
                "streamSid": self.stream_sid,
                "mark": {"name": uuid.uuid4().hex}}

    async def handle(self, websocket):
        """
        Handle every message in websocket until we receive a stop message or barf.
        """
        async for message in websocket:
            message = json.loads(message)
            if message["event"] == "connected":
                util.log(f"Received event 'connected': {message}")
            elif message["event"] == "start":
                util.log(f"Received event 'start': {message}")
                if self.stream_sid and self.stream_sid != message['streamSid']:
                    raise Exception("Unexpected new streamSid")
                self.stream_sid = message['streamSid']
            elif message["event"] == "media":
                util.log("Received event 'media'")
                # This assumes we get messages in order, we should instead
                # verify the sequence numbers. message["sequenceNumber"]
                self.receive_media(message)
                # # Send media back, for testing.
                # await websocket.send(
                #     json.dumps(
                #         payload_to_message(message["media"]["payload"])))
                # Send mark message, for testing. We should receive this back.
                await websocket.send(json.dumps(self.mark_message()))
            elif message["event"] == "stop":
                util.log(f"Received event 'stop': {message}")
                self.stream_sid = None
                break
            else:
                util.log(f"Received unexpected event: {message}")
        util.log("Connection closed")

    async def start(self):
        async with websockets.serve(self.handle, host, port):
            await asyncio.Future()  # run forever

async def main():
    server = Server()
    await server.start()

asyncio.run(main())
