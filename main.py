import numpy as np
from audio_input import init_audio, find_freq, freq_to_color
from display_qr import run_display
from color_names import print_results

## To do:
# control VLC
# Control LED strip


# Set audio stream parameters
RATE = 44100  # samples per second
CHUNK = 4096  # number of samples per frame

def main():
    stream = init_audio(RATE, CHUNK)

    print("Reading audio stream...")
    while True:
        # Read audio stream
        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
        # Find the dominant frequency with smoothing
        freq = find_freq(data, RATE, CHUNK)
        # Translate audio frequency to color
        color = freq_to_color(freq)
        # Display color shifting QR code
        run_display(color)

        print_results(freq, color)


    stream.stop_stream()
    stream.close()
    p.terminate()




if __name__ == '__main__':
    main()
