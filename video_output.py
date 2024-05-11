import cv2
import time


def display_frame(cap, playback_speed, frame_count, delay, resize=True):

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

    if resize:  # Trim the frame to widescreen
        frame = trim_widescreen(frame)

    # Display the frame
    cv2.imshow("Video", frame)
    if cv2.waitKey(delay) & 0xFF == ord("q"):  # Wait based on the video's fps
        return "break"

    return "ok"


def trim_widescreen(frame):
    # Get dimensions of the original frame
    height, width = frame.shape[:2]

    # New dimensions targeting 16:9 aspect ratio
    new_width = width
    new_height = int(new_width * 9 / 16)

    # Calculate cropping (assuming black bars are at the top and bottom)
    start_row = int((height - new_height) / 2)
    end_row = start_row + new_height

    # Crop the frame to the new dimensions
    cropped_frame = frame[start_row:end_row, :]

    # Resize to fill the screen if necessary (can adjust the dimensions as needed)
    resized_frame = cv2.resize(cropped_frame, (new_width, new_height))

    return resized_frame
