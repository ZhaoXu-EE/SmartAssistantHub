import pyaudio
import wave
import numpy as np
import time
from array import array
from collections import deque

class VoiceRecorder:
    def __init__(self):
        self.CHUNK = 1024  # 每次读取的音频块大小
        self.FORMAT = pyaudio.paInt16  # 16位格式
        self.CHANNELS = 1  # 单声道
        self.RATE = 44100  # 采样率
        self.THRESHOLD = 3000  # 声音检测阈值
        self.SILENCE_LIMIT = 2  # 静音判定秒数
        self.PREV_AUDIO = 0.5  # 保留之前的音频秒数
        
    def is_silent(self, data_chunk):
        """判断音频块是否为静音"""
        return max(data_chunk) < self.THRESHOLD
    
    def record(self, filename="output.wav"):
        """开始录音并进行语音检测"""
        print("* 正在初始化录音设备...")
        
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                       channels=self.CHANNELS,
                       rate=self.RATE,
                       input=True,
                       frames_per_buffer=self.CHUNK)
        
        print("* 录音开始，请说话...")
        
        audio_buffer = []
        rel = array('h')
        cur_data = ''
        silent_time = 0
        started = False
        
        # 用于存储之前的音频
        prev_audio = deque(maxlen=int(self.PREV_AUDIO * self.RATE / self.CHUNK))
        
        while True:
            data = stream.read(self.CHUNK)
            cur_data = array('h', data)
            silent = self.is_silent(cur_data)
            
            if not started:
                if not silent:
                    print("* 检测到声音，开始记录...")
                    started = True
                    # 添加之前缓存的音频
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
        
        print("* 检测到静音，录音结束")
        
        # 停止并关闭流
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # 保存录音文件
        self.save_audio(audio_buffer, filename)
        
    def save_audio(self, audio_buffer, filename):
        """保存录音到文件"""
        print(f"* 正在保存录音到 {filename}...")
        
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(pyaudio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        
        audio_buffer = [item for sublist in audio_buffer for item in sublist]
        wf.writeframes(array('h', audio_buffer).tobytes())
        wf.close()
        
        print("* 录音已保存")

if __name__ == "__main__":
    recorder = VoiceRecorder()
    recorder.record()