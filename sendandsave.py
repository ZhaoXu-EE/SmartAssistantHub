# main.py

import time
import sys
import asyncio
from six.moves import input
import os
import json
import logging

from azure.iot.device.aio import IoTHubModuleClient, IoTHubDeviceClient, ProvisioningDeviceClient

from package.utility import *
from package.basecomnios import *
from package.gsensor import *
from package.rfssensor import *
from package.thresholdcontroller import *

# Import the temperature control module
from temperature_control import TemperatureController, start_temperature_monitor

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Configuration
KASA_DEVICE_IP = "192.168.137.240"  # Replace with your Kasa device's IP address
TEMPERATURE_THRESHOLD = 28.0       # Temperature threshold in degrees Celsius
CHECK_INTERVAL = 10                # Interval to check temperature in seconds
TEMPERATURE_FILE = "last_rfs_message.json"  # Path to the temperature data file

# Global Instances
isEdge = False
isReal = False

model_id = "dtmi:Terasic:FCC:DE10_Nano;1"
useComponent = True

control_bridge = None
data_bridge = None
gs = Gsensor(name="gSensor", real=False)
rfs = RfsSensor(name='rfsSensors', real=False)
thc = ThresholdController(real=False)

async def execute_property_listener(client):
    global isEdge, data_bridge, thc
    if not isEdge:
        while True:
            patch = await client.receive_twin_desired_properties_patch()  # blocking call
            prop_dict = thc.update_component_property(data_bridge, patch)
            logger.debug(prop_dict)
            await client.patch_twin_reported_properties(prop_dict)
    else:
        async def edge_twin_patch_handler(patch):
            prop_dict = thc.update_component_property(data_bridge, patch)
            logger.debug(prop_dict)
            await client.patch_twin_reported_properties(prop_dict)
        client.on_twin_desired_properties_patch_received = edge_twin_patch_handler

async def provision_device(provisioning_host, id_scope, registration_id, symmetric_key, model_id):
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        symmetric_key=symmetric_key,
    )

    provisioning_device_client.provisioning_payload = {"modelId": model_id}
    return await provisioning_device_client.register()

async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception(
                f"The sample requires Python 3.5.3+. Current version of Python: {sys.version}"
            )
        print("IoT Hub Client for Python")
        hostname = os.uname().nodename  # Assuming hostname is needed
        logger.debug(f'DEBUG ::: Check {hostname}')
        delay = 10
        watchdog_task = None
        global isEdge, isReal, control_bridge, data_bridge, gs, rfs, thc

        if "IOTEDGE_IOTHUBHOSTNAME" in os.environ:
            isEdge = True
        else:
            isEdge = False

        if isEdge:
            print("Azure IoT Edge with PnP!")
            client = IoTHubModuleClient.create_from_edge_environment(product_info=model_id)
        else:
            switch = os.getenv("IOTHUB_DEVICE_SECURITY_TYPE")
            if switch == "DPS":
                provisioning_host = (
                    os.getenv("IOTHUB_DEVICE_DPS_ENDPOINT")
                    if os.getenv("IOTHUB_DEVICE_DPS_ENDPOINT")
                    else "global.azure-devices-provisioning.net"
                )
                id_scope = os.getenv("IOTHUB_DEVICE_DPS_ID_SCOPE")
                registration_id = os.getenv("IOTHUB_DEVICE_DPS_DEVICE_ID")
                symmetric_key = os.getenv("IOTHUB_DEVICE_DPS_DEVICE_KEY")

                registration_result = await provision_device(
                    provisioning_host, id_scope, registration_id, symmetric_key, model_id
                )

                if registration_result.status == "assigned":
                    print("Device was assigned")
                    print(registration_result.registration_state.assigned_hub)
                    print(registration_result.registration_state.device_id)
                    client = IoTHubDeviceClient.create_from_symmetric_key(
                        symmetric_key=symmetric_key,
                        hostname=registration_result.registration_state.assigned_hub,
                        device_id=registration_result.registration_state.device_id,
                        product_info=model_id,
                    )
                else:
                    raise RuntimeError(
                        "Could not provision device. Aborting Plug and Play device connection."
                    )

            elif switch == "connectionString":
                conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
                print(f"Connecting using Connection String {conn_str}")
                client = IoTHubDeviceClient.create_from_connection_string(
                    conn_str, product_info=model_id
                )
            else:
                raise RuntimeError(
                    "At least one choice needs to be made for complete functioning of this sample."
                )

        # Connect the client
        await client.connect()

        if "de10nano" in hostname:
            gs = Gsensor(name='gSensor', real=True)
            bridges = get_nios_status(hostname)
            if bridges[0] is not None:
                logger.debug('DEBUG ::: The FPGA is ready!')
                isReal = True
                control_bridge = bridges[0]
                data_bridge = bridges[1]
                rfs = RfsSensor(name='rfsSensors', real=True, offset=0x40100)
                thc = ThresholdController(real=True, bridge=data_bridge, offset=0x40200)
                watchdog_task = asyncio.create_task(watchdog_nios(control_bridge, 1))

        # Send initial values to Azure
        init_patch = {
            'thresholdProperty': {
                '__t': 'c',
                'lux': {'min': 0, 'max': 1000},
                'humidity': {'min': 0, 'max': 49.9},
                'temperature': {'min': 0, 'max': 42.3},
                'ax': {'min': -100, 'max': 100},
                'ay': {'min': -100, 'max': 100},
                'az': {'min': -100, 'max': 100},
                'gx': {'min': -10, 'max': 10},
                'gy': {'min': -10, 'max': 10},
                'gz': {'min': -10, 'max': 10},
                'mx': {'min': -100, 'max': 100},
                'my': {'min': -100, 'max': 100},
                'mz': {'min': -100, 'max': 100}
            },
            "$version": 1
        }
        init_dict = thc.update_component_property(data_bridge, init_patch)
        await client.patch_twin_reported_properties(init_dict)

        # Schedule tasks for listeners
        listener_tasks = asyncio.gather(
            execute_property_listener(client)
        )

        async def send_telemetry():
            print(f'Sending telemetry from the provisioned device every {delay} seconds')
            while True:
                try:
                    if isReal:
                        gs_data = gs.get_telemetries()
                        rfs_data = rfs.get_telemetries(data_bridge)
                    else:
                        gs_data = {
                            "gSensor": {
                                'x': thc.generate_module_dummy_value('X'),
                                'y': thc.generate_module_dummy_value('Y'),
                                'z': thc.generate_module_dummy_value('Z')
                            }
                        }
                        rfs_data = {
                            'lux': thc.generate_module_dummy_value('lux'),
                            'humidity': thc.generate_module_dummy_value('humidity'),
                            'temperature': thc.generate_module_dummy_value('temperature'),
                            'mpu9250': {
                                'ax': thc.generate_module_dummy_value('ax'),
                                'ay': thc.generate_module_dummy_value('ay'),
                                'az': thc.generate_module_dummy_value('az'),
                                'gx': thc.generate_module_dummy_value('gx'),
                                'gy': thc.generate_module_dummy_value('gy'),
                                'gz': thc.generate_module_dummy_value('gz'),
                                'mx': thc.generate_module_dummy_value('mx'),
                                'my': thc.generate_module_dummy_value('my'),
                                'mz': thc.generate_module_dummy_value('mz')
                            }
                        }

                    # Create telemetry messages
                    gs_msg = gs.create_component_telemetry(gs_data)
                    rfs_msg = rfs.create_component_telemetry(rfs_data)

                    # Send to cloud
                    await client.send_message(gs_msg)
                    logger.info(f'Sent message: {gs_msg}')
                    await client.send_message(rfs_msg)
                    logger.info(f'Sent message: {rfs_msg}')

                    # Convert messages to JSON strings and save locally (separately)
                    gs_msg_str = gs_msg.data.decode('utf-8') if isinstance(gs_msg.data, bytes) else gs_msg.data
                    rfs_msg_str = rfs_msg.data.decode('utf-8') if isinstance(rfs_msg.data, bytes) else rfs_msg.data

                    with open('last_gs_message.json', 'w', encoding='utf-8') as f_gs:
                        json.dump(json.loads(gs_msg_str), f_gs, ensure_ascii=False, indent=4)

                    with open('last_rfs_message.json', 'w', encoding='utf-8') as f_rfs:
                        json.dump(json.loads(rfs_msg_str), f_rfs, ensure_ascii=False, indent=4)

                except Exception as e:
                    logger.error(f'Error sending telemetry: {e}')

                finally:
                    await asyncio.sleep(delay)

        send_telemetry_task = asyncio.create_task(send_telemetry())

        # Initialize and start temperature controller
        temperature_controller = TemperatureController(
            device_ip=KASA_DEVICE_IP,
            temperature_threshold=TEMPERATURE_THRESHOLD,
            check_interval=CHECK_INTERVAL,
            temperature_file=TEMPERATURE_FILE
        )
        await temperature_controller.setup()
        temperature_monitor_task = asyncio.create_task(temperature_controller.monitor_temperature())

        # Define user input listener
        def stdin_listener():
            while True:
                try:
                    selection = input("Press Q to quit\n")
                    if selection.lower() == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(delay)

        # Run user input listener in executor
        loop = asyncio.get_running_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to finish
        await user_finished

        # Cancel all tasks
        send_telemetry_task.cancel()
        temperature_monitor_task.cancel()

        # Cancel listener tasks
        listener_tasks.add_done_callback(lambda r: r.exception())
        listener_tasks.cancel()

        if watchdog_task is not None:
            watchdog_task.cancel()

        # Finally, disconnect
        await client.disconnect()

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    # If using Python 3.7 or above, use the following code:
    asyncio.run(main(), debug=True)
