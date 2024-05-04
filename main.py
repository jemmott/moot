from audio_input import audio_processor
from video_output import video_display
from color_output import color_display
import queue
import threading



def main():
    speed_queue = queue.Queue(maxsize=10)
    color_queue = queue.Queue(maxsize=10)

    # Start threads
    video_thread = threading.Thread(target=video_display, args=(speed_queue,))
    color_thread = threading.Thread(target=color_display, args=(color_queue,))
    audio_thread = threading.Thread(
        target=audio_processor,
        args=(
            speed_queue,
            color_queue,
        ),
    )

    video_thread.start()
    color_thread.start()
    audio_thread.start()

    video_thread.join()
    color_thread.join()
    audio_thread.join()


if __name__ == "__main__":
    main()
