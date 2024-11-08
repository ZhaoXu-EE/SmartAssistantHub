import pyaudio
import wave
import numpy as np

# 配置参数
FORMAT = pyaudio.paInt16
CHANNELS = 1  # 单声道
RATE = 16000  # 采样率
CHUNK = 1024  # 每次读取的帧数
THRESHOLD = 500  # 音量阈值
SILENCE_LIMIT = 2  # 停止录音的静默时长（秒）

def is_silent(data, threshold):
    """判断当前帧是否静默"""
    audio_data = np.frombuffer(data, dtype=np.int16)
    return np.abs(audio_data).mean() < threshold

def record_to_file(filename):
    """录音并保存为 WAV 文件"""
    audio = pyaudio.PyAudio()

    print("初始化录音...")
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("开始录音...")
    frames = []
    silent_chunks = 0

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

        # 检测当前帧是否静默
        if is_silent(data, THRESHOLD):
            silent_chunks += 1
        else:
            silent_chunks = 0

        # 如果静默帧达到设定时长，则停止录音
        if silent_chunks > (SILENCE_LIMIT * RATE / CHUNK):
            print("检测到静默，录音结束。")
            break

    # 停止和关闭流
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 保存录音文件
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"录音已保存为 {filename}")

if __name__ == "__main__":
    output_filename = "output.wav"
    record_to_file(output_filename)
