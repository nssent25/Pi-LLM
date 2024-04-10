import pyaudio
import wave
import threading

class AudioRecorder:
    def __init__(self, filename="recording.wav", format=pyaudio.paInt16, channels=1, rate=44100, chunk=1024):
        self.filename = filename
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.frames = []
        self.is_recording = False
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.recording_thread = None

    def start_recording(self):
        if self.is_recording:
            print("Already recording!")
            return

        self.is_recording = True
        self.frames = []
        self.stream = self.audio.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)

        self.recording_thread = threading.Thread(target=self.record)
        self.recording_thread.start()
        print("Recording started.")

    def record(self):
        while self.is_recording:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            self.frames.append(data)

    def stop_recording(self):
        if not self.is_recording:
            print("Recording is not active!")
            return

        self.is_recording = False
        self.recording_thread.join()

        self.stream.stop_stream()
        self.stream.close()

        self.save_recording()
        print("Recording stopped and saved.")

    def save_recording(self):
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def close(self):
        self.audio.terminate()

    def play_audio(self, file_path):
        """
        Plays an audio file from a given path.

        :param file_path: Path to the audio file to be played.
        """
        wf = wave.open(file_path, 'rb')
        stream = self.audio.open(format=self.audio.get_format_from_width(wf.getsampwidth()),
                                 channels=wf.getnchannels(),
                                 rate=wf.getframerate(),
                                 output=True)

        data = wf.readframes(self.chunk)
        while data:
            stream.write(data)
            data = wf.readframes(self.chunk)

        stream.stop_stream()
        stream.close()
        wf.close()
        print(f"Playback finished for {file_path}.")
# # Usage example:

# # Create an instance of the AudioRecorder class
# audio_recorder = AudioRecorder(filename="test_recording.wav")

# # Start recording
# audio_recorder.start_recording()

# # Simulate recording for 10 seconds
# import time
# time.sleep(10)

# # Stop recording
# audio_recorder.stop_recording()

# # Clean up resources
# audio_recorder.close()
