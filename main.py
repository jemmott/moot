from audio_input import init_audio, audio_processor, freq_to_speed, freq_to_color
from video_output import display_frame
from color_names import closest_color
import queue
import threading
import cv2


def main():
    # Load video
    cap = cv2.VideoCapture("MOOT.mov")
    fps = cap.get(cv2.CAP_PROP_FPS)  # Get the frames per second of the video
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    delay = int(1000 / fps)  # Calculate delay for each frame in milliseconds

    # set up audio stream and queue
    stream = init_audio()
    frequency_queue = queue.Queue(maxsize=1)
    threading.Thread(
        target=audio_processor, args=(stream, frequency_queue), daemon=True
    ).start()

    # set initial values
    frequency = 100
    color = (0, 0, 0)
    playback_speed = 1

    while True:
        # Get new frequency if it exists
        if not frequency_queue.empty():
            frequency = frequency_queue.get_nowait()
            color = freq_to_color(frequency)
            playback_speed = freq_to_speed(frequency)

            print(
                f"Frequency: {frequency:.1f} Hz, Color: {closest_color(color)}, Speed: {playback_speed:.1f}x"
            )

        # Show video
        status = display_frame(cap, playback_speed, frame_count, delay)
        if status == "continue":
            continue
        elif status == "break":
            break

        # Do LED stuff

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
