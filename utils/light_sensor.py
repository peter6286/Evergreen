import board
import adafruit_bh1750

class LightSensor:
    def __init__(self):
        self.i2c = board.I2C()
        self.sensor = adafruit_bh1750.BH1750(self.i2c)

    def read_light(self):
        return self.sensor.lux
