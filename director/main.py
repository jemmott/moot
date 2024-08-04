"""
TO DO
- Map distance to playback speed
- Send params to MQTT
"""
# import board
# import adafruit_vl53l1x
import pyaudio
import numpy as np
import audio
import params

# testing only
import testing_distance_mock

vl53 = testing_distance_mock.get_distance()


def main():

    # distance sensor setup
    # i2c = board.I2C()  # uses board.SCL and board.SDA
    # vl53 = adafruit_vl53l1x.VL53L1X(i2c)
    # vl53.start_ranging()

    # Initialize PyAudio
    p = pyaudio.PyAudio()
    pa_stream = p.open(
        format=pyaudio.paFloat32, channels=1, rate=params.SAMPLING_RATE, output=True
    )

    theremin = audio.Theremin()

    mode = "standby"  # start mode

    try:
        while True:
            distance = vl53.distance

            mode, freq, amplitude, smoothed_dist, waveform = theremin.update(
                mode, distance
            )

            pa_stream.write(waveform.astype(np.float32).tobytes())
    finally:
        pa_stream.stop_stream()
        pa_stream.close()
        p.terminate()


if __name__ == "__main__":
    main()
