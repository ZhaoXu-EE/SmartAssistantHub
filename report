# Smart Assistant Hub Development Report

## Introduction &#x20;

The **Smart Assistant Hub** project was developed to address the increasing demand for integrated smart home systems that combine environmental monitoring, device control, and conversational AI capabilities. Leveraging both the DE10-Nano development board and Raspberry Pi, this project aimed to create a versatile and interactive hub for users to manage home environments intelligently and efficiently. The final implementation also considered practical constraints, such as hardware compatibility and cloud dependency, to ensure a robust and reliable solution. &#x20;

## Motivation &#x20;

Modern consumers desire seamless interaction with technology to simplify their daily lives. By incorporating advanced features such as voice interaction, environmental sensors, and cloud connectivity, the Smart Assistant Hub fulfills this need. This project also serves as a learning opportunity for embedded systems development, cloud integration, and addressing real-world hardware limitations. &#x20;

## Objectives &#x20;

1. Provide real-time environmental monitoring and data display. &#x20;
2. Enable voice-controlled smart home device management. &#x20;
3. Integrate conversational AI for dynamic user interaction. &#x20;

---

## System Design &#x20;

### Hardware Components &#x20;

- **DE10-Nano Development Board**: Acts as the central processing hub, managing sensor data and cloud communication. &#x20;
- **Raspberry Pi**: Used to overcome the DE10-Nano's limitations in audio processing, such as the lack of an audio codec. &#x20;
- \*\*Sensors  \*\*:
  - **DHT22**: Measures temperature and humidity. &#x20;
  - **MQ-135**: Detects air quality. &#x20;
- **USB Microphone and Speaker**: Enables voice interaction. &#x20;
- **Smart Plug (TP-Link Kasa HS103)**: Provides control over home appliances like lights and heaters, via the `python-kasa` library. &#x20;

### Software Components &#x20;

- **Audio Processing**: Utilized PyAudio for recording and playback, configured using PortAudio libraries. The Raspberry Pi's support for USB audio devices ensured smooth audio handling. &#x20;
- \*\*Speech-to-Text (STT) and Text-to-Speech (TTS)  \*\*:
  - **Cloud-Based STT**: Implemented via OpenAI Whisper API. &#x20;
  - **TTS**: Used OpenAI’s speech synthesis API for generating audio responses. &#x20;
- \*\*Cloud Integration  \*\*:
  - Connected to Microsoft Azure IoT Hub for uploading environmental data and managing devices. &#x20;
  - Azure Stream Analytics and Power BI were employed for data visualization and insights. &#x20;
- **Control Logic**: Developed Python scripts to interpret voice commands and manage device actions. &#x20;

---

## Implementation &#x20;

### Challenges and Solutions &#x20;

#### 1. **Audio Processing on DE10-Nano** &#x20;

- **Problem**: The DE10-Nano lacks built-in audio codec support and compatibility with the ALSA framework. &#x20;
- **Solution**: Shifted audio handling to Raspberry Pi, which supports USB audio devices natively. Configured the environment using PyAudio and validated audio functionality with test scripts. This ensured smooth voice interaction. &#x20;

#### 2. **WiFi Connectivity Issues** &#x20;

- **Problem**: DE10-Nano failed to recognize WiFi signals on higher channels, which disrupted the network setup. &#x20;
- **Solution**: Adjusted the WiFi hotspot channel on the host PC to a lower value (channel 6), enabling DE10-Nano’s connectivity. &#x20;

#### 3. **Temperature Monitoring and Control** &#x20;

- **Problem**: Delayed sensor data updates from the cloud impacted real-time monitoring. &#x20;
- **Solution**: Implemented a local JSON storage system to maintain the latest sensor data, reducing dependency on cloud latency. &#x20;

### Development Process &#x20;

1. \*\*Hardware Setup  \*\*:
   - Configured DE10-Nano and Raspberry Pi with necessary peripherals. &#x20;
   - Integrated DHT22 and MQ-135 sensors for environmental data collection. &#x20;
2. \*\*Software Configuration  \*\*:
   - Installed PortAudio, PyAudio, and PyGame for audio functionality on Raspberry Pi. &#x20;
   - Developed Python modules for voice recording (`record.py`) and smart plug control (`temperature_control.py`). &#x20;
3. \*\*Cloud Integration  \*\*:
   - Registered IoT devices on Azure IoT Hub and established secure connections. &#x20;
   - Enabled bi-directional communication for sensor data upload and command execution. &#x20;
4. \*\*Voice Interaction  \*\*:
   - Used OpenAI Whisper API for accurate transcription of commands. &#x20;
   - Processed commands for controlling smart devices or engaging in conversation via ChatGPT API. &#x20;

---

## Results &#x20;

### Key Achievements &#x20;

- Successfully implemented real-time environmental monitoring with cloud synchronization. &#x20;
- Enabled voice-controlled operations such as: &#x20;
  - Turning smart plugs on/off. &#x20;
  - Querying temperature and humidity data. &#x20;
  - Dynamic conversations using conversational AI. &#x20;
- Data visualization achieved through Azure’s Stream Analytics and Power BI. &#x20;

### Performance Metrics &#x20;

- **Audio Recording**: Achieved seamless voice capture and playback with minimal latency. &#x20;
- \*\*Cloud Data Transmission  \*\*:
  - Average upload time for sensor data: \~2 seconds. &#x20;
  - Successful MQTT messaging for device control. &#x20;
- \*\*User Interaction  \*\*:
  - High accuracy in voice command recognition (\~95%). &#x20;

---

## Discussion &#x20;

The Smart Assistant Hub has redefined smart home integration by bridging gaps in environmental monitoring, device interaction, and conversational AI. While the DE10-Nano’s hardware constraints presented challenges, the incorporation of Raspberry Pi ensured smooth operation. Cloud dependency remains a potential risk for critical functionalities; future iterations could include edge computing solutions to mitigate this issue. Fine-tuning the large language model for specific scenarios and adding distributed sensor nodes are promising directions for further development. &#x20;

---

## Conclusion &#x20;

The Smart Assistant Hub demonstrates the potential of combining embedded systems with cloud and AI technologies to create a robust and user-friendly smart home solution. This project provides a strong foundation for future enhancements, including support for additional smart devices and improved local processing capabilities. &#x20;

---

## Acknowledgments &#x20;

Special thanks to the technical support team for their guidance and to all contributors who provided hardware and software resources. Gratitude is extended to OpenAI and Microsoft Azure for their APIs and platforms that enabled key functionalities. &#x20;

## References &#x20;

- Project Repository: [GitHub - SmartAssistantHub](https://github.com/ZhaoXu-EE/SmartAssistantHub)                   &#x20;
- OpenAI APIs: [platform.openai.com](https://platform.openai.com)                                 &#x20;
- Azure IoT Hub Documentation: [Microsoft Azure IoT Hub](https://azure.microsoft.com/en-us/products/iot-hub)                                 &#x20;

