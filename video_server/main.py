from video_output import display_frame, display_black
import cv2
import subprocess
import paho.mqtt.client as mqtt
import threading
import sys
from queue import Queue

fullscreen = True
use_playback_delay = False

cap = cv2.VideoCapture("MOOT.mov")
cap_boot = cv2.VideoCapture("Startup_1.mov")
cap_shutdown = cv2.VideoCapture("Shutdown_1.mov")

#housekeeping
subprocess.Popen(["unclutter", "-idle", "1.0"])

if use_playback_delay:
    delay = 1  # play as fast as possible
else:
    fps = cap.get(cv2.CAP_PROP_FPS)  # Get the frames per second of the video
    if fps == 0:
        delay = 33
    else:
        delay = int(1000 / fps)  # Calculate delay for each frame in milliseconds

# PAUL HAXX
delay = 4

window_name = "video"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

if fullscreen:
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

speed_queue = Queue()
speed = 1

mode_queue = Queue()
mode = "standby"


def mqtt_thread():
    def on_message(client, userdata, msg):
        if msg.topic == "moot/speed":
            new_speed = float(msg.payload.decode())
            # print(f"speed update: {new_speed}")
            speed_queue.put(new_speed)

        if msg.topic == "moot/mode":
            new_mode = str(msg.payload.decode())
            # print(f"mode update: {new_mode}")
            mode_queue.put(new_mode)

    mqtt_broker = "192.168.0.200"
    client = mqtt.Client()
    client.on_message = on_message
    while True:
        try:
            client.connect(mqtt_broker, 1883, 60)
            break
        except:
            sys.stderr.write("cannot connect to mqtt")
    client.subscribe("moot/speed")
    client.subscribe("moot/mode")
    client.loop_forever()


# Starting MQTT thread
threading.Thread(target=mqtt_thread, daemon=True).start()

try:
    previous_mode = "standby"
    while True:
        if not speed_queue.empty():
            speed = speed_queue.get()

        if not mode_queue.empty():
            mode = mode_queue.get()

        if mode == "standby":
            status = display_black(cap, delay)

        elif mode == "boot":
            playback_speed = 1
            if previous_mode != "boot":
                cap_boot.set(cv2.CAP_PROP_POS_FRAMES, 1)
            status = display_frame(cap_boot, playback_speed, delay)

        elif mode == "shutdown":
            playback_speed = 1
            if previous_mode != "shutdown":
                cap_shutdown.set(cv2.CAP_PROP_POS_FRAMES, 1)
            status = display_frame(cap_shutdown, playback_speed, delay)

        # add boot and shutdown modes here (load videos, reset frame counts when active / standby, set speed to 1)
        else:
            playback_speed = 10 * speed + 1
            status = display_frame(cap, playback_speed, delay)

        previous_mode = mode

        key = cv2.waitKey(delay) & 0xFF
        if key == 27:  # ESC key
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
