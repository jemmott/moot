import numpy as np
import sounddevice as sd

# Constants
sample_rate = 44100  # Sample rate in Hz
frequency = 300  # Frequency in Hz
duration = 5  # Duration in seconds

# Generate time array
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
# Generate sine wave
waveform = 0.5 * np.sin(2 * np.pi * frequency * t)

# Play audio
sd.play(waveform, sample_rate)
sd.wait()  # Wait until the sound has finished playing
