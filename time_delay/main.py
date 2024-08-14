import cv2
import numpy as np
from collections import deque

# Set the time delay in seconds
time_delay = 20

# Initialize the video capture
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS) or 30
frame_delay = int(fps * time_delay)
frame_queue = deque(maxlen=frame_delay)

fullscreen = False
cv2.namedWindow("Delayed Video", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Delayed Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.setWindowProperty("Delayed Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

# Set the resolution of the monitor
monitor_resolution = (1920, 1080)  # Change this to your monitor's resolution

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame from webcam.")
        break

    frame_queue.append(frame)

    if len(frame_queue) == frame_delay:
        delayed_frame = frame_queue.popleft()
    else:
        delayed_frame = np.zeros(
            frame.shape, dtype=np.uint8
        )  # Ensures the frame is black

    # Resize the frame to match the monitor's resolution
    resized_frame = cv2.resize(delayed_frame, monitor_resolution)

    cv2.imshow("Delayed Video", resized_frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break
    if key == ord("f"):
        fullscreen = not fullscreen
        window_property = cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL
        cv2.setWindowProperty("Delayed Video", cv2.WND_PROP_FULLSCREEN, window_property)

cap.release()
cv2.destroyAllWindows()
