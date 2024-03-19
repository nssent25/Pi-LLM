# import pyaudio
# import wave
# import threading

# class AudioRecorder:
#     def __init__(self, sample_rate=48000, chunk=1024, sample_format=pyaudio.paInt16, channels=1):
#         self.sample_rate = sample_rate
#         self.chunk = chunk
#         self.sample_format = sample_format
#         self.channels = channels
#         self.frames = []

#         self.p = pyaudio.PyAudio()
#         self.stream = self.p.open(format=self.sample_format,
#                                   channels=self.channels,
#                                   rate=self.sample_rate,
#                                   frames_per_buffer=self.chunk,
#                                   input=True)

#         self.recording_thread = threading.Thread(target=self.record)
#         self.is_recording = False

#     def record(self):
#         while self.is_recording:
#             data = self.stream.read(self.chunk)
#             self.frames.append(data)

#     def start_recording(self):
#         self.is_recording = True
#         self.recording_thread.start()

#     def stop_recording(self):
#         self.is_recording = False
#         self.stream.stop_stream()
#         self.stream.close()
#         self.p.terminate()

#     def save_recording(self, filename):
#         wf = wave.open(filename, 'wb')
#         wf.setnchannels(self.channels)
#         wf.setsampwidth(self.p.get_sample_size(self.sample_format))
#         wf.setframerate(self.sample_rate)
#         wf.writeframes(b''.join(self.frames))
#         wf.close()

#     def get_raw_data(self):
#         return b''.join(self.frames)
    
import sounddevice as sd
import numpy as np
import threading

class AudioRecorder:
    def __init__(self, sample_rate=48000, chunk=1024, channels=1):
        self.sample_rate = sample_rate
        self.chunk = chunk
        self.channels = channels
        self.frames = []

        self.recording_thread = threading.Thread(target=self.record)
        self.is_recording = False

    def record(self):
        def callback(indata, frames, time, status):
            if status:
                print(status)
            self.frames.append(indata.copy())

        with sd.InputStream(callback=callback, channels=self.channels, samplerate=self.sample_rate):
            while self.is_recording:
                sd.sleep(self.chunk)

    def start_recording(self):
        self.is_recording = True
        self.recording_thread.start()

    def stop_recording(self):
        self.is_recording = False

    def save_recording(self, filename):
        np.save(filename, self.frames, allow_pickle=True)

    def get_raw_data(self):
        return np.concatenate(self.frames)