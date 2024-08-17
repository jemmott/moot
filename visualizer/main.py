import curses
import time
import random
import paho.mqtt.client as mqtt
import threading

# Global variables to hold the current speed and mode
speed = 0.5  # From -1 to 1
mode = "ACTIVE"  # Change this to "BOOT", "SHUTDOWN", "STANDBY", etc.

# Lock to manage access to shared variables
l = threading.Lock()

# Function to draw the frame
def draw_frame(win):
    rows, cols = win.getmaxyx()
    win.border("|", "|", "-", "-", "+", "+", "+", "+")
    win.addstr(
        0,
        (cols // 2) - len("MOOT: Matter Out Of Time") // 2,
        "MOOT: Matter Out Of Time",
    )
    win.refresh()


# Function to create the UV meter
def draw_meter(win, y, x, value, max_value, label):
    width = 20
    fill = int((value / max_value) * width)
    meter = "[" + "#" * fill + "-" * (width - fill) + "]"
    win.addstr(y, x, f"{label}: {meter}")


# Function to create ASCII art text
def draw_big_text(win, y, x, text):
    big_text = {
        "S": ["#####", "#    ", "#####", "    #", "#####"],
        "H": ["#   #", "#   #", "#####", "#   #", "#   #"],
        "U": ["#   #", "#   #", "#   #", "#   #", "#####"],
        "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  "],
        "D": ["#### ", "#   #", "#   #", "#   #", "#### "],
        "O": ["#####", "#   #", "#   #", "#   #", "#####"],
        "W": ["#   #", "#   #", "# # #", "## ##", "#   #"],
        "N": ["#   #", "##  #", "# # #", "#  ##", "#   #"],
        "A": ["#####", "#   #", "#####", "#   #", "#   #"],
        "C": ["#####", "#    ", "#    ", "#    ", "#####"],
        "E": ["#####", "#    ", "#####", "#    ", "#####"],
        "L": ["#    ", "#    ", "#    ", "#    ", "#####"],
        "I": [" ### ", "  #  ", "  #  ", "  #  ", " ### "],
        "V": ["#   #", "#   #", " # # ", " # # ", "  #  "],
        "R": ["#####", "#   #", "#####", "#  # ", "#   #"],
        "P": ["#####", "#   #", "#####", "#    ", "#    "],
        "G": ["#####", "#    ", "# ###", "#   #", "#####"],
        "B": ["#####", "#   #", "#####", "#   #", "#####"],
        "Y": ["#   #", " # # ", "  #  ", "  #  ", "  #  "],
    }

    for i, line in enumerate(zip(*[big_text[char] for char in text])):
        win.addstr(y + i, x, "  ".join(line))


# Function to create a simple waveform display
def draw_waveform(win, y, x, amplitude, width=40):
    wave = "".join(["-" if random.random() > amplitude else " " for _ in range(width)])
    win.addstr(y, x, wave)


# Function to update the display
def update_display(stdscr):
    global speed, mode
    curses.curs_set(0)
    stdscr.clear()

    while True:
        stdscr.clear()

        draw_frame(stdscr)

        # Draw mode in big letters
        draw_big_text(stdscr, 2, 5, mode)

        # Draw UV meter for speed
        draw_meter(stdscr, 10, 5, (speed + 1) / 2, 1, "Speed (seconds per second)")

        # Draw waveform
        draw_waveform(stdscr, 14, 5, speed)

        stdscr.refresh()
        time.sleep(0.1)


# MQTT on_message callback
def on_message(client, userdata, msg):
    global speed, mode, l
    if not l.acquire(blocking=False):
        return
    try:
        if msg.topic == "moot/speed":
            speed = float(msg.payload.decode())
        elif msg.topic == "moot/mode":
            mode = msg.payload.decode().upper()
    finally:
        l.release()


# Function to start MQTT loop
def start_mqtt():
    mqtt_broker = "192.168.0.200"
    mqtt_topic = ["moot/speed", "moot/mode"]

    client = mqtt.Client()
    client.on_message = on_message

    client.connect(mqtt_broker, 1883, 60)
    [client.subscribe(t) for t in mqtt_topic]

    # Start the MQTT client loop in a separate thread
    client.loop_start()


if __name__ == "__main__":
    # Start the MQTT loop
    start_mqtt()

    # Start the curses application
    curses.wrapper(update_display)
