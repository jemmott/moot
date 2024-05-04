import pyaudio
import numpy as np
from scipy.signal import find_peaks
from collections import deque
from color_names import closest_color


# Set audio stream parameters
RATE = 44100  # samples per second
CHUNK = 4096  # number of samples per frame
window_size = 5  # Number of past frequencies to consider
freq_window = deque(maxlen=window_size)


def audio_processor(speed_queue, color_queue):
    stream = init_audio(RATE, CHUNK)
    while True:
        # Read audio stream
        data = np.frombuffer(
            stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16
        )
        # Find the dominant frequency with smoothing
        freq = find_freq(data, RATE, CHUNK)
        # Translate audio frequency to color, speed
        color = freq_to_color(freq)
        playback_speed = freq_to_speed(freq)

        print(f"Frequency: {freq:.1f} Hz, Color: {closest_color(color)}, Speed: {playback_speed:.1f}x")

        add_to_queue(speed_queue, playback_speed)
        add_to_queue(color_queue, color)


def add_to_queue(q, value):
    # Ensure only the latest data is in the queue
    while q.full():
        try:
            q.get_nowait()  # Try to empty the queue quickly
        except queue.Empty:
            pass  # If the queue is already empty, do nothing
    q.put(value)


def init_audio(rate, chunk):
    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # List audio devices and prompt user to pick one
    list_audio_devices(p)
    mic_index = int(input("Please enter the index of your microphone: "))

    # Open audio stream
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=rate,
        input=True,
        input_device_index=mic_index,
        frames_per_buffer=chunk,
    )
    return stream


def list_audio_devices(p):
    print("Available audio devices:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(
            f"Index: {info['index']}, Name: {info['name']}, Input Channels: {info['maxInputChannels']}, Output Channels: {info['maxOutputChannels']}"
        )


def find_freq(audio_chunk, rate, chunk):
    # Perform FFT
    fft_data = np.fft.fft(audio_chunk)
    fft_data = np.abs(
        fft_data[: len(fft_data) // 2]
    )  # Take just the real part and normalize

    # Find peaks
    peaks, _ = find_peaks(fft_data, height=10)

    if peaks.size != 0:
        # Estimate dominant frequency
        dominant_freq = np.argmax(fft_data[peaks])  # Index of dominant frequency
        freq = peaks[dominant_freq] * rate / chunk  # Convert index to frequency
    else:
        freq = 118  # Not sure this is right.

    # Smooth the frequency with a moving average
    freq_window.append(freq)
    smoothed_freq = sum(freq_window) / len(freq_window)
    return smoothed_freq


def freq_to_color(freq):
    norm_freq = normalize_frequency(freq)

    color = (int((1 - norm_freq) * 255), 0, int(norm_freq * 255))
    return color


def freq_to_speed(freq):
    norm_freq = normalize_frequency(freq)

    color = 5 * norm_freq - 5  # This needs some tuning
    return color


def normalize_frequency(freq, f_min=50):
    f_max = f_min * (2**7)  # 7 octaves higher
    log_f_min = np.log(f_min)
    log_f_max = np.log(f_max)

    # Map the frequency to a value between 0 and 1 on a log scale
    norm_freq = np.clip((np.log(freq) - log_f_min) / (log_f_max - log_f_min), 0, 1)
    return norm_freq
