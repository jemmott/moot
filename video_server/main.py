from video_output import display_frame
import cv2
import paho.mqtt.client as mqtt
import threading
from queue import Queue

# Initial settings
fullscreen = True
use_playback_delay = False

# Open video file
cap = cv2.VideoCapture("MOOT.mov")
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
delay = int(1000 / fps) if fps > 0 else 33

# Window setup
window_name = "MOOT VID"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  # Start as normal to set properties
if fullscreen:
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# MQTT setup
speed_queue = Queue()
speed = 1

def mqtt_thread():
    def on_message(client, userdata, msg):
        if msg.topic == "moot/speed":
            new_speed = float(msg.payload.decode())
            print(f"speed update: {new_speed}")
            speed_queue.put(new_speed)

    mqtt_broker = "192.168.0.200"
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(mqtt_broker, 1883, 60)
    client.subscribe("moot/speed")
    client.loop_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()

try:
    while True:
        if not speed_queue.empty():
            speed = speed_queue.get()

        playback_speed = 10 * speed + 1
        ret, frame = cap.read()
        if not ret:
            break  # Stop if video is over or fails

        cv2.imshow(window_name, frame)
        key = cv2.waitKey(delay) & 0xFF
        if key == 27:  # ESC key
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
