import cv2
import time
import numpy as np


def display_frame_core(frame, delay):
    # Display the frame
    cv2.imshow("video", frame)
    if cv2.waitKey(delay) & 0xFF == ord("q"):  # Wait based on the video's fps
        return "break"


def display_frame(cap, playback_speed, delay):
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

    # print(current_frame)

    # Calculate new frame position based on playback_speed
    new_frame = current_frame + int(playback_speed)
    if new_frame < 0:
        new_frame = frame_count - 100  # Correct for underflow to enable reverse looping
    if new_frame >= frame_count:
        new_frame = 0

    # Set the new frame position
    cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

    # Read the frame
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        return "continue"

    display_frame_core(frame, delay)

    return "ok"


def display_black(cap, delay):
    # Create a black screen
    frame = np.zeros(
        (
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            3,
        ),
        dtype=np.uint8,
    )

    display_frame_core(frame, delay)

    return "ok"
