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

    def __init__(self, media_callback):
        self._stream_sid = None
        self._media_callback = media_callback

    async def receive_media(self, message):
        media = message["media"]
        chunk = base64.b64decode(media["payload"])
        self._media_callback(chunk)

    # async def send_media(self, chunk):
    #     payload = base64.encode(chunk)
    #     await self._websocket.send(
    #         json.dumps(
    #             {"event": "media",
    #              "streamSid": self._stream_sid,
    #              "media": {"payload": payload}}))

    def mark_message(self):
        """
        Return a mark message which can be sent to the Twilio websocket.
        """
        return {"event": "mark",
                "streamSid": self._stream_sid,
                "mark": {"name": uuid.uuid4().hex}}

    async def consumer_handler(self, websocket):
        """
        Handle every message in websocket until we receive a stop
        message or barf.
        """
        async for message in websocket:
            message = json.loads(message)
            if message["event"] == "connected":
                util.log(f"Received event 'connected': {message}")
            elif message["event"] == "start":
                util.log(f"Received event 'start': {message}")
                if self._stream_sid and self._stream_sid != message['streamSid']:
                    raise Exception("Unexpected new streamSid")
                self._stream_sid = message['streamSid']
            elif message["event"] == "media":
                #util.log("Received event 'media'")
                # This assumes we get messages in order, we should instead
                # verify the sequence numbers. message["sequenceNumber"]
                await self.receive_media(message)
                # Send mark message, for testing.
                # We should receive this back.
                # XXX use the producer handler
                #await websocket.send(
                #    json.dumps(self.mark_message()))
            elif message["event"] == "stop":
                util.log(f"Received event 'stop': {message}")
                self._stream_sid = None
                # XXX Must stop server/protocol here, or it just lives on.
                break
            else:
                pass
                #util.log(f'Received unexpected event: {message["event"]}')
        util.log("Connection closed")

    async def producer_handler(self, websocket):
        await asyncio.Future()  # run forever

    async def handle(self, websocket):
        await asyncio.gather(
            self.consumer_handler(websocket),
            self.producer_handler(websocket))

    async def start(self):
        async with websockets.serve(self.handle, host, port):
            await asyncio.Future()  # run forever
