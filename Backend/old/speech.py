# speech.py
# This program records an audio file using a usb microphone and then returns it as an mp3 to be processed by the backend

import pyaudio
import wave
import threading

# Set the sample rate and other parameters
sample_rate = 44100  # Hertz
chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2

p = pyaudio.PyAudio()  # Create an interface to PortAudio

# Start the stream
stream = p.open(format=sample_format,
                channels=channels,
                rate=sample_rate,
                frames_per_buffer=chunk,
                input=True)

frames = []  # Initialize array to store frames

# Create a function to handle recording
def record():
    while True:
        data = stream.read(chunk)
        frames.append(data)

# Start the recording function in a separate thread
recording_thread = threading.Thread(target=record)
recording_thread.start()

# Wait for a stop signal from the backend
stop_signal = input("Press Enter to stop recording...")

# Stop the stream and recording thread
stream.stop_stream()
stream.close()

# Terminate the PortAudio interface
p.terminate()

# Save the recorded data as a WAV file
wf = wave.open('output.wav', 'wb')
wf.setnchannels(channels)
wf.setsampwidth(p.get_sample_size(sample_format))
wf.setframerate(sample_rate)
wf.writeframes(b''.join(frames))
wf.close()