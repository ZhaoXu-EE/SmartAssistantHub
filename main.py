from record import VoiceRecorder
from openai import OpenAI
import pygame

recorder = VoiceRecorder()
client = OpenAI()
COUNT = 2

for _ in range(COUNT):

    recorder.record()

    audio_file= open("/home/xu/workspace/SmartAssistantHub/temporary.wav", "rb")
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
    )
    print(transcription.text)

    if "turn on the light" in transcription.text.lower():
        message_content = "the light is on"
        print(message_content)
    if "temperature" in transcription.text.lower():
        message_content = "the temperature is 26 degrees Celsius"
        print(message_content)
    else: 

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": transcription.text
                }
            ]
        )
        message_content = completion.choices[0].message.content
        print(message_content)

    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=message_content,
    )
    output_path = "output.mp3"
    with open(output_path, "wb") as f:
        try:
            for chunk in response.iter_bytes():
                f.write(chunk)
            print(f"Audio successfully saved to {output_path}")
        except AttributeError:
            print("Stream method not available. Falling back to non-streaming download...")
            f.write(response.content)

    pygame.mixer.init()
    pygame.mixer.music.load('/home/xu/workspace/SmartAssistantHub/output.mp3')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # Wait for music to finish playing
        continue