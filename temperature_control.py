# temperature_control.py

import json
import asyncio
import logging
from kasa import SmartPlug

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Configuration
KASA_DEVICE_IP = "192.168.137.240"  
TEMPERATURE_THRESHOLD = 28.0       # Temperature threshold in degrees Celsius
CHECK_INTERVAL = 10                # Interval to check temperature in seconds
TEMPERATURE_FILE = "last_rfs_message.json"  # Path to the temperature data file

class TemperatureController:
    def __init__(self, device_ip, temperature_threshold, check_interval, temperature_file):
        self.device_ip = device_ip
        self.temperature_threshold = temperature_threshold
        self.check_interval = check_interval
        self.temperature_file = temperature_file
        self.plug = SmartPlug(self.device_ip)
        self.switch_on = False  # Track the current state of the switch

    async def setup(self):
        """Initialize the connection to the Kasa device."""
        try:
            await self.plug.update()
            logger.info(f"Successfully connected to Kasa device at {self.device_ip}")
        except Exception as e:
            logger.error(f"Error connecting to Kasa device: {e}")

    async def turn_on(self):
        """Turn on the Kasa switch."""
        if not self.switch_on:
            try:
                await self.plug.turn_on()
                self.switch_on = True
                logger.info("Kasa switch turned ON")
            except Exception as e:
                logger.error(f"Error turning on Kasa switch: {e}")

    async def turn_off(self):
        """Turn off the Kasa switch."""
        if self.switch_on:
            try:
                await self.plug.turn_off()
                self.switch_on = False
                logger.info("Kasa switch turned OFF")
            except Exception as e:
                logger.error(f"Error turning off Kasa switch: {e}")

    async def read_temperature(self):
        """Read the temperature from the local JSON file."""
        try:
            with open(self.temperature_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Full JSON data: {data}")
                temperature = data.get('temperature', None)
                if temperature is not None:
                    logger.debug(f"Current Temperature: {temperature}°C")
                    return temperature
                else:
                    logger.warning("Temperature data not found in JSON file")
                    return None
        except Exception as e:
            logger.error(f"Error reading temperature data: {e}")
            return None



    async def monitor_temperature(self):
        """Monitor the temperature and control the Kasa switch accordingly."""
        while True:
            temperature = await self.read_temperature()
            if temperature is not None:
                if temperature >= self.temperature_threshold:
                    logger.info(f"Temperature {temperature}°C exceeds or equals threshold. Turning ON the switch.")
                    await self.turn_on()
                elif temperature < self.temperature_threshold:
                    logger.info(f"Temperature {temperature}°C is below threshold. Turning OFF the switch.")
                    await self.turn_off()
            await asyncio.sleep(self.check_interval)  # Wait before the next check

async def start_temperature_monitor():
    """Initialize and start the temperature monitoring."""
    controller = TemperatureController(
        device_ip=KASA_DEVICE_IP,
        temperature_threshold=TEMPERATURE_THRESHOLD,
        check_interval=CHECK_INTERVAL,
        temperature_file=TEMPERATURE_FILE
    )
    await controller.setup()
    await controller.monitor_temperature()
