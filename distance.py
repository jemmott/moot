import board
import adafruit_vl53l1x
import numpy as np
import pyaudio
import pixelblaze


# Constants
SAMPLE_RATE = 44100  # Sample rate in Hz
MAX_FREQ = 440.0    # Max frequency in Hz
MIN_FREQ = 50.0      # Min frequency in Hz
MAX_DIST = 100.0     # Max expected distance in cm (adjust based on your setup)
MIN_DIST = 0.0       # Min expected distance in cm
FRAME_LENGTH = 1 / 50.0  # Frame length to match the sensor's update rate, maybe wrong

def map_distance_to_frequency(distance):
    # Currently linear, probably should be log?
    if not distance or distance > MAX_DIST:
        distance = MAX_DIST
    return MIN_FREQ + (MAX_FREQ - MIN_FREQ) * (distance - MIN_DIST) / (MAX_DIST - MIN_DIST)

def generate_sine_wave(freq, length, rate):
    t = np.linspace(0, length, int(rate * length), False)
    return 0.5 * np.sin(2 * np.pi * freq * t)

