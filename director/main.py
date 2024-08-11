import pyaudio
import board
import adafruit_vl53l1x
import numpy as np
import audio
import params
import paho.mqtt.client as mqtt
import testing_distance_mock

sensor_mock = False  # True to run with a mock sensor
logging = True

def main():

    # distance sensor setup
    if sensor_mock:
        vl53 = testing_distance_mock.get_distance()
    else:
        i2c = board.I2C()  # uses board.SCL and board.SDA
        vl53 = adafruit_vl53l1x.VL53L1X(i2c)
        vl53.start_ranging()

    client = mqtt.Client()
    client.connect("localhost", 1883, 60)

    # Initialize PyAudio
    p = pyaudio.PyAudio()
    pa_stream = p.open(
        format=pyaudio.paFloat32, channels=1, rate=params.SAMPLING_RATE, output=True
    )

    theremin = audio.Theremin()

    mode = "standby"  # start mode

    try:
        while True:
            try:
                distance = vl53.distance
            except Exception as E:
                distance = None
                print(f"Ahhhh, snap. Theremin reports {E}")

            mode, freq, amplitude, speed, waveform = theremin.update(
                mode, distance
            )

            client.publish("moot/mode", mode)
            client.publish("moot/speed", freq / params.MAX_FREQ)

            pa_stream.write(waveform.astype(np.float32).tobytes())

            if logging:
                print(f"Time Travel Mode: {mode}, Time Speed: {speed} (seconds per second), frequency {freq} (inverse seconds), theremin loudness {amplitude}")

    finally:
        pa_stream.stop_stream()
        pa_stream.close()
        p.terminate()


if __name__ == "__main__":
    main()
