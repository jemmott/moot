import time


def color_display(color_queue):
    color = (0, 0, 0)
    while True:
        while not color_queue.empty():
            color = color_queue.get_nowait()

        time.sleep(0.1)
