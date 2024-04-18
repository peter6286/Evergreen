import serial
import time

class PlantMonitor:
    def __init__(self):
        self.ser = serial.Serial("/dev/serial0", 9600)
        self.wetness = 0
        self.temp = 0
        self.humidity = 0
        self.delay_period = 0.1

    def get_wetness(self):
        self.send("w")
        return self.wetness

    def get_temp(self):
        self.send("t")
        return self.temp

    def get_humidity(self):
        self.send("h")
        return self.humidity

    def send(self, message):
        self.ser.write(bytes(message + "\n", 'utf-8'))
        time.sleep(self.delay_period)
        self._wait_for_message()

    def _wait_for_message(self):
        time.sleep(self.delay_period)  # Give the sensor time to respond
        incoming_message = self.ser.readline().decode().strip()
        if '=' in incoming_message:
            code, value = incoming_message.split('=')
            if code == "w":
                self.wetness = float(value)
            elif code == "t":
                self.temp = float(value)
            elif code == "h":
                self.humidity = float(value)
