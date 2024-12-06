from azure.eventhub import EventHubConsumerClient
import json
import threading

def consume_events_once(connection_str, consumer_group, eventhub_name):
    """
    消费 EventHub 中的事件，接收到一个包含 temperature 数据的事件后停止，并返回温度值。
    
    参数:
    - connection_str: EventHub 的连接字符串
    - consumer_group: 消费者组名称
    - eventhub_name: EventHub 实体名称

    返回:
    - 如果接收到 temperature 数据，返回对应的浮点数值；
    - 如果超时未接收到数据，返回 None。
    """
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

# 示例调用
if __name__ == "__main__":
    CONNECTION_STR = "Endpoint=sb://ihsuprodblres091dednamespace.servicebus.windows.net/;SharedAccessKeyName=service;SharedAccessKey=Z9zblrF/Vg9RjbVy3kDL4tfPGNvV4RUkLAIoTEUck1E=;EntityPath=iothub-ehub-xuzhao-hub-62321561-165c11c2a1"
    CONSUMER_GROUP = "$Default"
    EVENTHUB_NAME = "iothub-ehub-xuzhao-hub-62321561-165c11c2a1"

    temperature = consume_events_once(CONNECTION_STR, CONSUMER_GROUP, EVENTHUB_NAME)
    if temperature is not None:
        print(f"Received temperature: {temperature}")
    else:
        print("No temperature data received.")
