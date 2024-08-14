import paho.mqtt.client as mqtt
from pixelblaze import Pixelblaze
import json, threading

# Pixelblaze setup
pixelblaze_ip = "192.168.0.205"
print(f"waiting on pixelblaze at {pixelblaze_ip}")
pb = Pixelblaze(pixelblaze_ip)
print("pb connected")

# pb.setActivePatternByName("standby")

l = threading.Lock()
global cur_mode
cur_mode = None

# Define the callback function to handle incoming MQTT messages
def on_message(client, userdata, msg):
    global cur_mode, l
    if not l.acquire(blocking=False):
        return
    try:
        if msg.topic == "moot/speed":
            speed = float(msg.payload.decode())
            print(f"speed update: {speed}")
            pb.setActiveVariables({"speed": speed})
        if msg.topic == "moot/brightness":
            b = float(msg.payload.decode())
            pb.setBrightnessSlider(b)
            print(f"brightness update: {b}")
        if msg.topic == "moot/mode":
            mode = msg.payload.decode()
            if mode == cur_mode:
                return
            print(f"mode update: {mode}")
            # if mode == "active": mode = "activealt"
            pb.setActivePatternByName(mode)
            cur_mode = mode
    finally:
        l.release()


# MQTT setup
mqtt_broker = "192.168.0.200"
mqtt_topic = ["moot/speed", "moot/brightness", "moot/mode"]

client = mqtt.Client()
client.on_message = on_message

client.connect(mqtt_broker, 1883, 60)
[client.subscribe(t) for t in mqtt_topic]

# Start the MQTT client loop
print("connected to MQTT and PixelBlaze, looping forever")
client.loop_forever()
