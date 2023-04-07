import asyncio
import unittest

import transcription

class TestStringMethods(unittest.IsolatedAsyncioTestCase):

    async def check_audio_generator_empty(self, bridge):
        """Return True if the audio_generator does not produce within a timeout."""
        try:
            await asyncio.wait_for(anext(bridge.audio_generator()), timeout=1.0)
        except asyncio.TimeoutError:
            return True
        else:
            return False

    async def test_audio_generator_terminated(self):
        """ The audio_generator method of a terminated bridge does not produce values."""
        bridge = transcription.SpeechClientBridge(None, None)
        bridge.terminate()
        async for i in bridge.audio_generator():
            self.fail()

    async def test_audio_generator_empty(self):
        """ The audio_generator method of a bridge with no requests does not produce values."""
        bridge = transcription.SpeechClientBridge(None, None)
        self.assertTrue(await self.check_audio_generator_empty(bridge))

    async def test_audio_generator_one(self):
        """ The audio_generator method of a bridge with one request produces one value."""
        in_val = 1
        bridge = transcription.SpeechClientBridge(None, None)
        bridge.add_request(in_val)
        out_val = await anext(bridge.audio_generator())
        self.assertEqual(bytes(in_val), out_val)
        self.assertTrue(await self.check_audio_generator_empty(bridge))

    async def test_audio_generator_two(self):
        """ The audio_generator method of a bridge with two requests produces one value."""
        in_vals = [1, 2]
        bridge = transcription.SpeechClientBridge(None, None)
        for i in in_vals:
            bridge.add_request(i)
        out_val = await anext(bridge.audio_generator())
        self.assertEqual(b"".join(bytes(i) for i in in_vals), out_val)
        self.assertTrue(await self.check_audio_generator_empty(bridge))


if __name__ == '__main__':
    unittest.main()
