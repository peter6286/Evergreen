from utils.light_sensor import LightSensor
from utils.plant_monitor import PlantMonitor
import time
import logging
import json
import os
import torch
import clip
from PIL import Image
import json
from torchvision.datasets import Flowers102
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



datadir = "/home/pi/Desktop/598_EverGreen"

def load_flower_data(img_transform=None):
    if os.path.isdir(datadir + "/flowers-102"):
        do_download = False
    else:
        do_download = True
    train_set = Flowers102(root=datadir, split='train', transform=img_transform, download=do_download)
    test_set = Flowers102(root=datadir, split='val', transform=img_transform, download=do_download)
    classes = json.load(open(osp.join(datadir, "flowers102_classes.json")))
    return train_set, test_set, classes

def classify_image(image_path, clip_model, clip_preprocess, device, flower_classes):
    image = Image.open(image_path)
    image_input = clip_preprocess(image).unsqueeze(0).to(device)
    text_inputs = torch.cat([clip.tokenize(f"a photo of a {c}, a type of flower.") for c in flower_classes]).to(device)
    with torch.no_grad():
        image_features = clip_model.encode_image(image_input)
        text_features = clip_model.encode_text(text_inputs)
    image_features /= image_features.norm(dim=-1, keepdim=True)
    text_features /= text_features.norm(dim=-1, keepdim=True)
    similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
    top_values, top_indices = similarity[0].topk(5)
    print("\nTop predictions:\n")
    for value, index in zip(top_values, top_indices):
        print(f"{flower_classes[index]:>16s}: {100 * value.item():.2f}%")
    most_likely_value, most_likely_index = similarity[0].topk(1)
    most_likely_flower = flower_classes[most_likely_index[0]]
    probability = most_likely_value[0].item() * 100
    return most_likely_flower, probability


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
    device = "cuda" if torch.cuda.is_available() else 'cpu'
    clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)
    image_path = "/home/pi/Desktop/598_EverGreen/rose.png"
    flower_train, flower_test, flower_classes = load_flower_data()
    
    print('Captured image path:', image_path)
    most_likely_flower, probability = classify_image(image_path, clip_model, clip_preprocess, device, flower_classes)
    print(f'Identified Plant Type: {most_likely_flower} with a probability of {probability:.2f}%')
    
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
            'Plant':most_likely_flower,
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
