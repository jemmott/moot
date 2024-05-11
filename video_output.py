import cv2
import time


# To Do: Loop not underflowing in reverse

def display_frame(cap, playback_speed, frame_count, delay):

    current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

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

    # Display the frame
    cv2.imshow("Video", frame)
    if cv2.waitKey(delay) & 0xFF == ord("q"):  # Wait based on the video's fps
        return "break"

    return "ok"
