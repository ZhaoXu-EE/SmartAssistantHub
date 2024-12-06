from record import VoiceRecorder
from openai import OpenAI
import pygame
from azure.eventhub import EventHubConsumerClient
import json
import threading
import asyncio
from kasa import Discover

recorder = VoiceRecorder()
client = OpenAI()
COUNT = 4
CONNECTION_STR = "Endpoint=sb://ihsuprodblres091dednamespace.servicebus.windows.net/;SharedAccessKeyName=service;SharedAccessKey=Z9zblrF/Vg9RjbVy3kDL4tfPGNvV4RUkLAIoTEUck1E=;EntityPath=iothub-ehub-xuzhao-hub-62321561-165c11c2a1"
CONSUMER_GROUP = "$Default"
EVENTHUB_NAME = "iothub-ehub-xuzhao-hub-62321561-165c11c2a1"


def consume_events_once(connection_str, consumer_group, eventhub_name):
    stop_event = threading.Event()  # 用于控制消费的标志变量
    temperature_value = None  # 用于存储接收到的 temperature 数据

    def on_event(partition_context, event):
        nonlocal temperature_value  # 使用外部变量存储 temperature 值
        if stop_event.is_set():
            return  # 如果已接收到目标事件，直接返回

        if event is None or not event.body_as_str().strip():
            return  # 忽略空事件

        try:
            data = json.loads(event.body_as_str())  # 将事件数据解析为 JSON
            if 'temperature' in data:  # 检查是否包含 temperature 数据
                try:
                    temperature_value = float(data['temperature'])  # 转换为浮点数
                    print(f"Temperature: {temperature_value}")  # 输出温度数据
                    stop_event.set()  # 标记已接收到目标事件
                    partition_context.update_checkpoint(event)  # 更新检查点
                except (ValueError, TypeError):
                    print("Received invalid temperature value.")  # 无法转换为浮点数时忽略
        except json.JSONDecodeError:
            pass  # 忽略非 JSON 数据

    client = EventHubConsumerClient.from_connection_string(
        connection_str,
        consumer_group,
        eventhub_name=eventhub_name
    )
    with client:
        # 使用后台线程检查 stop_event 标志，达到目的后停止接收
        def receiver():
            client.receive(
                on_event=on_event,
                starting_position="@latest",  # 从最新事件开始
            )
        receiver_thread = threading.Thread(target=receiver, daemon=True)
        receiver_thread.start()

        # 等待 stop_event 被设置，最多等待 30 秒（可根据需要调整）
        stop_event.wait(timeout=30)

        if not stop_event.is_set():
            print("No temperature data received within the timeout period.")
        
        return temperature_value


async def light_on():
    dev = await Discover.discover_single("192.168.137.240", username="2558852597@qq.com", password="Zx_20001102")
    await dev.turn_on()
    await dev.update()


async def light_off():
    dev = await Discover.discover_single("192.168.137.240", username="2558852597@qq.com", password="Zx_20001102")
    await dev.turn_off()
    await dev.update()


for _ in range(COUNT):

    recorder.record()

    audio_file= open("/home/xu/workspace/SmartAssistantHub/temporary.wav", "rb")
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
    )
    print(transcription.text)

    if "turn on the light" in transcription.text.lower():
        asyncio.run(light_on())
        message_content = "the light is on"
        print(message_content)
    elif "turn off the light" in transcription.text.lower():
        asyncio.run(light_off())
        message_content = "the light is off"
        print(message_content)
    elif "temperature" in transcription.text.lower():
        azure_temperature = consume_events_once(CONNECTION_STR, CONSUMER_GROUP, EVENTHUB_NAME)
        message_content = f"the temperature is {azure_temperature:.2f} degrees Celsius"
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