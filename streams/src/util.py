def log(msg):
    print(msg)

def wav_to_chunk(b):
    """Return wav bytes with header removed."""
    # ie only one chunk, we will probably need to split.
    #binarySound = bytearray()
    #binaryHeader = bytearray()
    #with open("a2002011001-e02.wav",'rb') as f:
        #binaryHeader = f.read(44)
        #binarySound = f.read()
    # The header length can vary depending on the fact chunk. Could skip to "data" plus 4?
    #https://www.twilio.com/blog/build-a-soundboard-using-gcp-speech-to-text-twilio-voice-media-streams-and-aspdotnet-core
    # usually 44, we have 58?
    #_header = f.read(58)
    #return f.read()
    return b[58:]
