from video_output import display_frame
import cv2
import numpy as np

# To Do
# Get MQTT client working

fullscreen = True
use_playback_delay = False


def toggle_fullscreen(window_name):
    global fullscreen
    fullscreen = not fullscreen
    if fullscreen:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    else:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)


def main():
    # Load video
    cap = cv2.VideoCapture("MOOT.mov")
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if use_playback_delay:
        delay = 1  # play as fast as possible
    else:
        fps = cap.get(cv2.CAP_PROP_FPS)  # Get the frames per second of the video
        if fps == 0:
            delay = 33
        else:
            delay = int(1000 / fps)  # Calculate delay for each frame in milliseconds

    window_name = "Video"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)

    if fullscreen:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    try:
        while True:
            playback_speed = -10
            status = display_frame(cap, playback_speed, frame_count, delay)

            # Check for key press
            key = cv2.waitKey(delay) & 0xFF
            if key == ord('f'):
                toggle_fullscreen(window_name)
            elif key == 27:  # ESC key to break the loop
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
