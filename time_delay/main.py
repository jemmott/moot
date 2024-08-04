import cv2
import numpy as np
from collections import deque

# Set the time delay in seconds
time_delay = 3

# Initialize the video capture with a fallback mechanism
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Using V4L2 backend

# Fallback to the default backend if V4L2 fails
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

# Verify if the webcam was opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Get the frame rate of the webcam
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0:
    fps = 30  # Default FPS if not available
frame_delay = int(fps * time_delay)

# Create a deque to store frames for the delay
frame_queue = deque(maxlen=frame_delay)

# Variable to track fullscreen state
fullscreen = False

# Create a named window
cv2.namedWindow("Delayed Video", cv2.WINDOW_GUI_NORMAL)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to read frame from webcam.")
        break

    # Add the frame to the deque
    frame_queue.append(frame)

    # If the deque is filled, get the oldest frame for delayed display
    if len(frame_queue) == frame_delay:
        delayed_frame = frame_queue.popleft()
        cv2.imshow("Delayed Video", delayed_frame)
    else:
        # Display black frames until the delay period is reached
        black_frame = np.zeros(frame.shape, dtype=np.uint8)
        cv2.imshow("Delayed Video", black_frame)

    key = cv2.waitKey(1) & 0xFF

    # Break the loop on 'q' key press
    if key == ord("q"):
        break

    # Toggle fullscreen on 'f' key press
    if key == ord("f"):
        fullscreen = not fullscreen
        if fullscreen:
            cv2.setWindowProperty(
                "Delayed Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
            )
        else:
            cv2.setWindowProperty(
                "Delayed Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL
            )

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
