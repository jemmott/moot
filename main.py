import pyaudio
import numpy as np
from scipy.signal import find_peaks
import pygame


## To do:
# Moving average
# control VLC
# Control LED strip


# Set audio stream parameters
RATE = 44100  # samples per second
CHUNK = 4096  # number of samples per frame

def main():
    stream = init_audio()

    print("Reading audio stream...")
    while True:
        # Read audio stream
        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)

        freq = find_freq(data, RATE, CHUNK)
        print(f'Dominant Frequency: {freq} Hz')
        color = freq_to_color(freq)
        display_color(color)
    stream.stop_stream()
    stream.close()
    p.terminate()


def init_audio():
    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # List audio devices and prompt user to pick one
    list_audio_devices(p)
    mic_index = int(input("Please enter the index of your microphone: "))

    # Open audio stream
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    input=True,
                    input_device_index=mic_index,
                    frames_per_buffer=CHUNK)
    return stream

def list_audio_devices(p):
    print("Available audio devices:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"Index: {info['index']}, Name: {info['name']}, Input Channels: {info['maxInputChannels']}, Output Channels: {info['maxOutputChannels']}")


def find_freq(audio_chunk, rate, chunk):
    # Perform FFT
    fft_data = np.fft.fft(audio_chunk)
    fft_data = np.abs(fft_data[:len(fft_data) // 2])  # Take just the real part and normalize

    # Find peaks
    peaks, _ = find_peaks(fft_data, height=10)

    if peaks.size != 0:
        # Estimate dominant frequency
        dominant_freq = np.argmax(fft_data[peaks])  # Index of dominant frequency
        freq = peaks[dominant_freq] * rate / chunk  # Convert index to frequency

    return freq


def freq_to_color(freq, f_min=50):
    f_max = f_min * (2 ** 7)  # 7 octaves higher
    log_f_min = np.log(f_min)
    log_f_max = np.log(f_max)

    # Map the frequency to a value between 0 and 1 on a log scale
    norm_freq = np.clip((np.log(freq) - log_f_min) / (log_f_max - log_f_min), 0, 1)

    color = (int((1 - norm_freq) * 255), 0, int(norm_freq * 255))
    return color


# Display frequency as color in window - this will get replaced with the LED strip code
pygame.init()
win = pygame.display.set_mode((200, 200))
def display_color(color):
    win.fill(color)
    pygame.display.update()



if __name__ == '__main__':
    main()
