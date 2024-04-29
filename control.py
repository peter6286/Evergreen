from utils.light_sensor import LightSensor
from utils.plant_monitor import PlantMonitor
import time
import logging
import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
from datetime import datetime
import lib8relind
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import os.path as osp

# Paths to the certificate files
ca = 'ver_key/AmazonRootCA1.pem'
private_key = 'ver_key/6228bf39f1582a64a893649a1d0f77eb4de1d7574afcdf38a3953c51437d7aa2-private.pem.key'
certificate = 'ver_key/6228bf39f1582a64a893649a1d0f77eb4de1d7574afcdf38a3953c51437d7aa2-certificate.pem.crt'
stack_level = 0  # Adjust based on your jumper settings
relay_number = 5  # Relay connected to the water pump
datadir = "/home/pi/Desktop/598_EverGreen"
image_path = osp.join(datadir, "rose.png")

# Define expanded flower classes
flower_classes = ['tulip', 'daisy', 'sunflower','daffodil','rose']

# Load a more lightweight model, e.g., MobileNetV2
model = models.mobilenet_v2(pretrained=True)
model.eval()  # Set the model to inference mode

# Optimize and enhance image transformations
transform = transforms.Compose([
    transforms.Resize(256),  # Increase slightly for better feature extraction
    transforms.CenterCrop(224),  # Standard size for MobileNet
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # Normalization for MobileNet
])


# Create and configure the MQTT client
myMQTTClient = AWSIoTMQTTClient("test_pi")
myMQTTClient.configureEndpoint("a31v04gy74znbf-ats.iot.us-east-2.amazonaws.com", 8883)
myMQTTClient.configureCredentials(ca, private_key, certificate)

# MQTT client connection setup
myMQTTClient.connect()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def classify_image(image_path, model, transform):
    # Load and preprocess the image
    image = Image.open(image_path).convert('RGB')
    image = transform(image)
    image = image.unsqueeze(0)  # Add batch dimension

    # Inference
    with torch.no_grad():
        outputs = model(image)
    # Get the prediction (simplified mapping to limited classes)
    _, predicted = torch.max(outputs, 1)
    predicted_class_index = predicted[0] % len(flower_classes)  # Modulo to limit to defined classes
    predicted_class = flower_classes[predicted_class_index]

    return predicted_class

def customCallback(client, userdata, message):
    """ Callback function that is called when an MQTT message is received. """
    payload = json.loads(message.payload.decode('utf-8'))
    command = payload.get('command', '')
    
    if command == 'start_pump':
        logging.info("Received command to start the pump")
        lib8relind.set(stack_level, relay_number, 1)
        time.sleep(1)  # Pump runs for 5 seconds
        lib8relind.set(stack_level, relay_number, 0)
        logging.info("Pump operation completed")

def main():

    predicted_class = classify_image(image_path, model, transform)
    print(f'Predicted Flower Type: {predicted_class}')
    
    myMQTTClient.subscribe("topic/command", 1, customCallback)
    light_sensor = LightSensor()
    plant_monitor = PlantMonitor()
    now = datetime.now()
    readable_time = now.strftime('%Y-%m-%d %H:%M:%S')
    while True:
        payload = {
            'plant':"Green Onion",
            'timestamp': readable_time,
            'temperature': plant_monitor.get_temp(),
            'humidity': plant_monitor.get_humidity(),     # Simulated humidity
            'light_level': round(light_sensor.read_light(),3) 
        }
        try:
            myMQTTClient.publish("topic/plant_health", json.dumps(payload), 0)
            logging.info("Sensor data published")
        except Exception as e:
            logging.error(f"Failed to publish sensor data: {e}")
        time.sleep(1200)

if __name__ == '__main__':
    try:
        myMQTTClient.connect()
        logging.info("Connected to AWS IoT")
        main()
    except Exception as e:
        logging.error(f"Failed to connect to AWS IoT: {e}")
        exit(1)
