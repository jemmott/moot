import board
import adafruit_vl53l1x
import numpy as np
import pyaudio
import pixelblaze


# Constants
SAMPLE_RATE = 44100  # Sample rate in Hz
MAX_FREQ = 2000.0    # Max frequency in Hz
MIN_FREQ = 200.0      # Min frequency in Hz
MAX_DIST = 100.0     # Max expected distance in cm (adjust based on your setup)
MIN_DIST = 0.0       # Min expected distance in cm

def map_distance_to_frequency(distance):
    # Currently linear, probably should be log?
    if not distance or distance > MAX_DIST:
        distance = MAX_DIST
    return MIN_FREQ + (MAX_FREQ - MIN_FREQ) * (distance - MIN_DIST) / (MAX_DIST - MIN_DIST)

def generate_sine_wave(freq, length, rate):
    t = np.linspace(0, length, int(rate * length), False)
    return 0.5 * np.sin(2 * np.pi * freq * t)

def main():
    current_phase = 0.0
    frame_length = 1 / 50.0  # Frame length to match the sensor's update rate, maybe wrong

    # initialize VL53
    i2c = board.I2C()  # uses board.SCL and board.SDA

    vl53 = adafruit_vl53l1x.VL53L1X(i2c)
    vl53.start_ranging()

    # Initialize PyAudio
    p = pyaudio.PyAudio()
    pa_stream = p.open(format=pyaudio.paFloat32, channels=1, rate=SAMPLE_RATE, output=True)

    pb = pixelblaze.Pixelblaze("pb-moot")
    #pb2 = pixelblaze.Pixelblaze("pb-ander")
    pb.setActivePattern("Interactive-forwards")

    try:
        while True:
            distance = vl53.distance
            freq = map_distance_to_frequency(distance)
            print(freq)
            pb.setActiveVariables({"t1":freq/1000})
            #pb2.setActiveVariables({"t1":freq/1000})
            waveform = generate_sine_wave(freq, frame_length, SAMPLE_RATE)
            pa_stream.write(waveform.astype(np.float32).tobytes())

    finally:
        pa_stream.stop_stream()
        pa_stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
