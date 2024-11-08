# Generate spoken audio from input text
# from pathlib import Path
# from openai import OpenAI
# client = OpenAI()

# speech_file_path = Path(__file__).parent / "speech.mp3"
# response = client.audio.speech.create(
#   model="tts-1",
#   voice="alloy",
#   input="Today is a wonderful day to build something people love!"
# )

# # response.stream_to_file(speech_file_path)       # 已弃用
# try:
#     with open(speech_file_path, 'wb') as f:
#         # 使用流式写入方法保存文件
#         for chunk in response.iter_bytes():  # 替代 `stream_to_file` 的方法
#             f.write(chunk)
#     print(f"Speech file saved at: {speech_file_path}")
# except AttributeError as e:
#     print(f"Error: {e}")
#     print("Falling back to non-streaming download...")
#     with open(speech_file_path, 'wb') as f:
#         f.write(response.content)

#----------------------------------------------------------------------------
#Streaming real time audio
from openai import OpenAI

client = OpenAI()

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello world! This is a streaming test.",
)

# response.stream_to_file("output.mp3")     # 已弃用
# 替代 stream_to_file 方法
output_path = "output.mp3"

# 手动处理流式响应并写入文件
with open(output_path, "wb") as f:
    try:
        # 假设 response 支持 iter_bytes 或类似的流式方法
        for chunk in response.iter_bytes():
            f.write(chunk)
        print(f"Audio successfully saved to {output_path}")
    except AttributeError:
        # 如果流式方法不可用，回退到直接写入整个内容
        print("Stream method not available. Falling back to non-streaming download...")
        f.write(response.content)