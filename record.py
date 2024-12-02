import pyaudio
import wave
import numpy as np
import time
from array import array
from collections import deque

class VoiceRecorder:
    def __init__(self):
        self.CHUNK = 1024  # Size of each audio chunk to read
        self.FORMAT = pyaudio.paInt16  # 16-bit format
        self.CHANNELS = 1  # Mono channel
        self.RATE = 44100  # Sampling rate
        self.THRESHOLD = 3000  # Sound detection threshold
        self.SILENCE_LIMIT = 2  # Number of seconds of silence before stopping
        self.PREV_AUDIO = 0.5  # Seconds of audio to prepend to the recording
        
    def is_silent(self, data_chunk):
        """Determines if the audio chunk is silence"""
        return max(data_chunk) < self.THRESHOLD
    
    def record(self, filename="temporary.wav"):
        """Starts recording with voice detection"""
        print("* Initializing audio device...")
        
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                       channels=self.CHANNELS,
                       rate=self.RATE,
                       input=True,
                       frames_per_buffer=self.CHUNK)
        
        print("* Recording started, please speak...")
        
        audio_buffer = []
        rel = array('h')
        cur_data = ''
        silent_time = 0
        started = False
        
        # Buffer for storing previous audio
        prev_audio = deque(maxlen=int(self.PREV_AUDIO * self.RATE / self.CHUNK))
        
        while True:
            data = stream.read(self.CHUNK)
            cur_data = array('h', data)
            silent = self.is_silent(cur_data)
            
            if not started:
                if not silent:
                    print("* Sound detected, recording started...")
                    started = True
                    # Add previously cached audio
                    audio_buffer.extend(list(prev_audio))
                    audio_buffer.append(cur_data)
                else:
                    prev_audio.append(cur_data)
                continue
            
            if silent:
                silent_time += 1
                if silent_time > int(self.SILENCE_LIMIT * self.RATE / self.CHUNK):
                    break
            else:
                silent_time = 0
            audio_buffer.append(cur_data)
        
        print("* Silence detected, recording stopped")
        
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save the recording
        self.save_audio(audio_buffer, filename)
        
    def save_audio(self, audio_buffer, filename):
        """Save the recording to a file"""
        print(f"* Saving recording to {filename}...")
        
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(pyaudio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        
        audio_buffer = [item for sublist in audio_buffer for item in sublist]
        wf.writeframes(array('h', audio_buffer).tobytes())
        wf.close()
        
        print("* Recording saved")

if __name__ == "__main__":
    recorder = VoiceRecorder()
    recorder.record()