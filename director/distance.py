import time
import board
import adafruit_vl53l1x
import paho.mqtt.client as mqtt
from params import MAX_FREQ



def main():

    # distance sensor setup
    i2c = board.I2C()  # uses board.SCL and board.SDA
    vl53 = adafruit_vl53l1x.VL53L1X(i2c)
    vl53.start_ranging()

    client = mqtt.Client()
    client.connect("localhost", 1883, 60)

    while True:
        d = vl53.distance
        d = d if d else 0
        print(f"reporting {d}")
        client.publish("moot/distance", d)
        client.publish("moot/speed", d/MAX_FREQ)
        time.sleep(1 / 25)

if __name__ == "__main__":
    main()
