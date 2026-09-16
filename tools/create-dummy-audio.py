"""Create short, harmless placeholder tones for the Birthday FM audio slots."""
import math
import os
import struct
import wave

FILES = [
    ("page-01-intro-01.wav", 440),
    ("page-03-track-01.wav", 523),
    ("page-03-track-02.wav", 587),
    ("page-03-track-03.wav", 659),
    ("page-03-track-04.wav", 698),
    ("page-03-track-05.wav", 784),
    ("page-05-final-broadcast-01.wav", 392),
]

os.makedirs("audio", exist_ok=True)
for filename, frequency in FILES:
    path = os.path.join("audio", filename)
    rate, seconds, volume = 44100, 1.2, 0.18
    frames = []
    for i in range(int(rate * seconds)):
        envelope = min(1, i / (rate * 0.05), (rate * seconds - i) / (rate * 0.1))
        frames.append(struct.pack("<h", int(32767 * volume * envelope * math.sin(2 * math.pi * frequency * i / rate))))
    with wave.open(path, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(rate)
        audio.writeframes(b"".join(frames))
    print(path)
