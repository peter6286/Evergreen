from utils.light_sensor import LightSensor
from utils.plant_monitor import PlantMonitor
from utils.camera_module import capture_image
import time

def main():
    light_sensor = LightSensor()
    plant_monitor = PlantMonitor()
    id = 1
    while True:
        # print('Time: ',id,'Sec')
        image_path = capture_image()
        print('captured image path: ',image_path)
        """
            ToDo: embed with the CV program to generate the plant type
        """
        # Read and print light intensity
        light_level = light_sensor.read_light()
        print(f"Light Intensity: {light_level:.2f} Lux")

        # Read and print plant conditions
        wetness = plant_monitor.get_wetness()
        temp = plant_monitor.get_temp()
        humidity = plant_monitor.get_humidity()
        print(f"Plant Wetness: {wetness}")
        print(f"Plant Temperature: {temp}°C")
        print(f"Plant Humidity: {humidity}%")

        print()
        time.sleep(5)
        id+= 5
        

if __name__ == '__main__':
    main()
