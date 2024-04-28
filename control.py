from utils.light_sensor import LightSensor
from utils.plant_monitor import PlantMonitor
import time
import logging
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
from datetime import datetime
import lib8relind

# Paths to the certificate files
ca = 'ver_key/AmazonRootCA1.pem'
private_key = 'ver_key/6228bf39f1582a64a893649a1d0f77eb4de1d7574afcdf38a3953c51437d7aa2-private.pem.key'
certificate = 'ver_key/6228bf39f1582a64a893649a1d0f77eb4de1d7574afcdf38a3953c51437d7aa2-certificate.pem.crt'
stack_level = 0  # Adjust based on your jumper settings
relay_number = 5  # Relay connected to the water pump

# Create and configure the MQTT client
myMQTTClient = AWSIoTMQTTClient("test_pi")
myMQTTClient.configureEndpoint("a31v04gy74znbf-ats.iot.us-east-2.amazonaws.com", 8883)
myMQTTClient.configureCredentials(ca, private_key, certificate)

# MQTT client connection setup
myMQTTClient.connect()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def customCallback(client, userdata, message):
    """ Callback function that is called when an MQTT message is received. """
    payload = json.loads(message.payload.decode('utf-8'))
    command = payload.get('command', '')
    
    if command == 'start_pump':
        logging.info("Received command to start the pump")
        lib8relind.set(stack_level, relay_number, 1)
        time.sleep(5)  # Pump runs for 5 seconds
        lib8relind.set(stack_level, relay_number, 0)
        logging.info("Pump operation completed")

def main():
    # Subscribe to the topic to listen for commands
    myMQTTClient.subscribe("topic/command", 1, customCallback)
    light_sensor = LightSensor()
    plant_monitor = PlantMonitor()
    now = datetime.now()
    readable_time = now.strftime('%Y-%m-%d %H:%M:%S')
    while True:
        light_sensor = LightSensor()
        plant_monitor = PlantMonitor()
        now = datetime.now()
        readable_time = now.strftime('%Y-%m-%d %H:%M:%S')
        payload = {
            'timestamp': readable_time,
            'temperature': plant_monitor.get_temp(),
            'humidity': plant_monitor.get_humidity(),     # Simulated humidity
            'light_level': round(light_sensor.read_light(),3)  # Simulated light level
        }
        try:
            myMQTTClient.publish("topic/plant_health", json.dumps(payload), 0)
            logging.info("Sensor data published")
        except Exception as e:
            logging.error(f"Failed to publish sensor data: {e}")
        time.sleep(60)

if __name__ == '__main__':
    try:
        myMQTTClient.connect()
        logging.info("Connected to AWS IoT")
        main()
    except Exception as e:
        logging.error(f"Failed to connect to AWS IoT: {e}")
        exit(1)
