import cv2
import numpy as np
from collections import deque
from screeninfo import get_monitors

# Get the screen resolution from the first monitor
screen_width, screen_height = get_monitors()[0].width, get_monitors()[0].height

# Set the time delay in seconds
time_delay = 1

# Initialize the video capture
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# Fallback and error checking
if not cap.isOpened():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

# Set frame rate
fps = cap.get(cv2.CAP_PROP_FPS) or 30
frame_delay = int(fps * time_delay)

# Queue for frame storage
frame_queue = deque(maxlen=frame_delay)

# Fullscreen flag
fullscreen = False
cv2.namedWindow('Delayed Video', cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame from webcam.")
        break

    frame_queue.append(frame)

    if len(frame_queue) == frame_delay:
        delayed_frame = frame_queue.popleft()
    else:
        delayed_frame = np.zeros(frame.shape, dtype=np.uint8)

    # Resize frame for fullscreen
    if fullscreen:
        delayed_frame = cv2.resize(delayed_frame, (screen_width, screen_height))

    cv2.imshow('Delayed Video', delayed_frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    if key == ord('f'):
        fullscreen = not fullscreen
        window_property = cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL
        cv2.setWindowProperty('Delayed Video', cv2.WND_PROP_FULLSCREEN, window_property)

cap.release()
cv2.destroyAllWindows()
