# Transcribe audio
from openai import OpenAI
client = OpenAI()

audio_file= open("/home/xu/workspace/SmartAssistantHub/output.wav", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file
)
print(transcription.text)