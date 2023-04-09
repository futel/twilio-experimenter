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
        """Yields media chunks with recieve_media()."""
        self._stream_sid = None
        self._send_queue = asyncio.Queue()
        self._recv_queue = asyncio.Queue()

    async def start(self):
        util.log("websocket server starting")
        async with websockets.serve(self.handle, host, port):
            await asyncio.Future()  # run forever

    async def receive_response(self):
        """Generator for received media chunks."""
        # XXX need to stop when there won't be any more
        while True:
            yield await self._recv_queue.get()

    def add_request(self, buffer):
        """Add a chunk of bytes to the sending queue."""
        buffer = bytes(buffer)
        self._send_queue.put_nowait(buffer)

    def _enqueue_media(self, message):
        """Add a chunk of bytes to the receiving queue."""
        media = message["media"]
        chunk = base64.b64decode(media["payload"])
        self._recv_queue.put_nowait(chunk)

    # def mark_message(self):
    #     """
    #     Return a mark message which can be sent to the Twilio websocket.
    #     """
    #     return {"event": "mark",
    #             "streamSid": self._stream_sid,
    #             "mark": {"name": uuid.uuid4().hex}}

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
                # verify the sequence numbers? Or just skip?
                # message["sequenceNumber"]
                self._enqueue_media(message)
            elif message["event"] == "stop":
                util.log(f"Received event 'stop': {message}")
                self._stream_sid = None
                break
            elif message["event"] == "mark":
                util.log(f"Received event 'mark': {message}")
        util.log("Connection closed")
        # XXX Must stop server/protocol here, or it just lives on, and other
        #     possible cleanup to prepare for restart.

    async def producer_handler(self, websocket):
        while True:
            chunk = await self._send_queue.get()
            payload = base64.b64encode(chunk).decode()
            util.log("sending")
            await websocket.send(
                json.dumps(
                    {"event": "media",
                     "streamSid": self._stream_sid,
                     "media": {"payload": payload}}))

    async def handle(self, websocket):
        # XXX we will need to restart if connection was closed?
        await asyncio.gather(
            self.consumer_handler(websocket),
            self.producer_handler(websocket))
