import cv2
import queue
import threading
import time


def frame_capture(video_source, frame_queue, capture_delay):
    cap = cv2.VideoCapture(video_source)
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            timestamp = time.time()
            if frame_queue.full():
                try:
                    frame_queue.get_nowait()  # Remove oldest frame if queue is full
                except queue.Empty:
                    pass
            frame_queue.put((timestamp, frame))
            time.sleep(capture_delay)
    finally:
        cap.release()


def frame_display(frame_queue, display_delay):
    fullscreen = False
    cv2.namedWindow("Video", cv2.WINDOW_NORMAL)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("f"):
            fullscreen = not fullscreen
            cv2.setWindowProperty(
                "Video",
                cv2.WND_PROP_FULLSCREEN,
                cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL,
            )

        current_time = time.time()
        target_time = current_time - display_delay

        # Remove old frames
        while not frame_queue.empty():
            timestamp, _ = frame_queue.queue[0]
            if timestamp < target_time:
                try:
                    frame_queue.get_nowait()
                except queue.Empty:
                    break
            else:
                break

        # Display the most relevant frame
        if not frame_queue.empty():
            _, frame = frame_queue.get()
            cv2.imshow("Video", frame)

    cv2.destroyAllWindows()


def main(video_source=0, capture_delay=0.03, display_delay=0.03, max_queue_size=10):
    frame_queue = queue.Queue(maxsize=max_queue_size)

    capture_thread = threading.Thread(
        target=frame_capture, args=(video_source, frame_queue, capture_delay)
    )
    capture_thread.start()

    try:
        frame_display(frame_queue, display_delay)
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        capture_thread.join()


if __name__ == "__main__":
    main()
