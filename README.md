# SmartAssistantHub
## De10-nano环境配置
### 1. 更新软件包
```bash
sudo apt update && sudo apt upgrade
```

### 2. 安装 PortAudio 开发库
安装 PortAudio 及其头文件：
```bash
sudo apt install libportaudio2 libportaudiocpp0 portaudio19-dev
```

### 3. 安装其他构建工具
确保你已经安装了必要的构建工具：
```bash
sudo apt install build-essential python3-dev
```

### 4. 再次尝试安装 PyAudio
现在重新运行 pip 安装命令：
```bash
pip install pyaudio
```

### 5. 验证安装
安装完成后，验证是否成功：
```bash
python3 -c "import pyaudio; print(pyaudio.__version__)"
```

### 6. 安装numpy并验证
安装完成后，验证是否成功：
```bash
pip install numpy
python3 -c "import numpy; print(numpy.__version__)"
```

### 7. 验证声卡
连接声卡后，验证是否成功接入：
```bash
lsusb | grep -i audio
```

### 8. 手动加载USB音频驱动模块
```bash
sudo modprobe snd-usb-audio
```

### 9. 检查Ångström Linux的内核是否有usb音频模块
```bash
ls /lib/modules/$(uname -r)/kernel/sound/usb/
```

## Raspberry Pi环境配置
### 0. 安装miniconda
```bash
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm ~/miniconda3/miniconda.sh
source ~/miniconda3/bin/activate
conda init --all
```
### 1. 更新软件包
```bash
sudo apt update && sudo apt upgrade
```
### 2. Install the required dependencies
```bash
sudo apt install portaudio19-dev python3-dev
```
### 3. Install PyAudio and Numpy
```bash
pip install pyaudio numpy
```
### 4. 验证声卡
连接声卡后，验证是否成功接入：
```bash
lsusb | grep -i audio
```
### 5. Install pygame to play audio file
```bash
pip install pygame
```