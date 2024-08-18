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
        curses.color_pair(1),
    )
    win.refresh()


# Function to create the UV meter
def draw_meter(win, y, x, value, max_value, label):
    width = 20
    fill = int((value / max_value) * width)
    meter = "[" + "#" * fill + "-" * (width - fill) + "]"
    win.addstr(y, x, f"{label}: {meter}", curses.color_pair(1))


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
        win.addstr(y + i, x, "  ".join(line), curses.color_pair(1))


# Function to create a simple waveform display
def draw_waveform(win, y, x, amplitude, width=40):
    wave = "".join(["-" if random.random() > amplitude else " " for _ in range(width)])
    win.addstr(y, x, wave, curses.color_pair(1))


def draw_matrix_effect(win, rows, cols):
    bottom_start = rows - (rows // 4)  # Focus on the bottom quarter of the screen
    matrix_columns = [bottom_start] * cols  # Initialize the start position for each column

    # Keep track of old positions to erase characters
    old_chars = []

    while True:
        # Erase old characters
        for old_y, old_x in old_chars:
            win.addstr(old_y, old_x, ' ', curses.color_pair(2))
        old_chars.clear()

        # Update multiple columns per frame for density
        for _ in range(cols // 2):
            x = random.randint(0, cols - 1)
            y = matrix_columns[x]

            # Gradually increase the density as it approaches the bottom
            if y < bottom_start + (rows // 10):
                if random.random() > 0.9:  # 50% chance to skip drawing for fading effect
                    continue

            # Choose a character
            char = random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

            # Draw the character within the boundaries (avoiding the frame)
            if y < rows - 1:
                win.addstr(y, x, char, curses.color_pair(2))
                # Save the position to be erased next time
                old_chars.append((y, x))

            # Update the position for the next frame
            matrix_columns[x] += 1

            # Reset the column before it reaches the bottom to avoid accumulation
            if matrix_columns[x] >= rows - 2:  # Stop before the last row to avoid overlap with the frame
                matrix_columns[x] = bottom_start + random.randint(-2, 2)  # Add some randomness to the reset point

        win.refresh()
        time.sleep(0.25)



# Function to update the display
def update_display(stdscr):
    global speed, mode
    curses.curs_set(0)
    stdscr.clear()

    # Initialize color pairs
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    while True:
        stdscr.clear()

        draw_frame(stdscr)

        # Draw mode in big letters
        draw_big_text(stdscr, 2, 5, mode)

        # Draw UV meter for speed
        draw_meter(stdscr, 10, 5, (speed + 1) / 2, 1, "Speed (seconds per second)")

        # Draw waveform
        draw_waveform(stdscr, 14, 5, speed)

        # Draw matrix effect at the bottom
        rows, cols = stdscr.getmaxyx()
        draw_matrix_effect(stdscr, rows, cols)

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
