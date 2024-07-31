from audio_input import freq_to_speed
from video_output import display_frame
from color_names import closest_color
from distance import map_distance_to_frequency, generate_sine_wave, SAMPLE_RATE, FRAME_LENGTH, MAX_FREQ
import board
import adafruit_vl53l1x
import queue
import threading
import cv2
import pixelblaze
import pyaudio
import numpy as np

fullscreen = True
use_playback_delay = False


def main():
    # Load video
    #cap = cv2.VideoCapture("hats.mov")
    #if not cap.isOpened():
    #    print("Error: Could not open video.")
    #    return
    #frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    #if use_playback_delay:
    #    delay = 1  # play as fast as possible
    #else:
    #    fps = cap.get(cv2.CAP_PROP_FPS)  # Get the frames per second of the video
    #    delay = int(1000 / fps)  # Calculate delay for each frame in milliseconds

    # set initial values
    freq = 100
    color = (0, 0, 0)
    playback_speed = 1
    status = "ok"

    #if fullscreen:
    #    cv2.namedWindow("Video", cv2.WND_PROP_FULLSCREEN)
    #    cv2.setWindowProperty("Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # distance sensor setup
    i2c = board.I2C()  # uses board.SCL and board.SDA
    vl53 = adafruit_vl53l1x.VL53L1X(i2c)
    vl53.start_ranging()

    # Initialize PyAudio
    p = pyaudio.PyAudio()
    pa_stream = p.open(format=pyaudio.paFloat32, channels=1, rate=SAMPLE_RATE, output=True)

    # LED setup
    pb = pixelblaze.Pixelblaze("pb-moot")
    pb.setActivePatternByName("Time Machine")

    try:
        while True:

            # FIXME this loop needs to be broken up into individual mqtt driven services

            distance = vl53.distance
            freq = map_distance_to_frequency(distance)

            # LED stuff
            pb.setActiveVariables({"speed":freq/MAX_FREQ})

            # audio out
            waveform = generate_sine_wave(freq, FRAME_LENGTH, SAMPLE_RATE)
            pa_stream.write(waveform.astype(np.float32).tobytes())

            # video out
            playback_speed = freq_to_speed(freq)
            #status = display_frame(cap, playback_speed, frame_count, delay)

            # "UI/UX"
            print(f"Frequency: {freq:.1f} Hz, Speed: {playback_speed:.1f}x")
            if status != "ok":
                break

            # TODO add state machine to drive pattern switcher

    finally:
        #cap.release()
        cv2.destroyAllWindows()
        pa_stream.stop_stream()
        pa_stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
