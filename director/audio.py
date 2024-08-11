import numpy as np
import params


def map_distance_to_frequency(distance):
    # Clamp the distance within the specified bounds
    clamped_distance = np.clip(distance, params.MIN_DISTANCE, params.MAX_DISTANCE)

    # Map the clamped distance using a logarithmic scale
    log_scale = np.log(clamped_distance)

    # Normalize the logarithmic value between 0 and 1
    normalized_log = (log_scale - np.log(params.MIN_DISTANCE)) / (
        np.log(params.MAX_DISTANCE) - np.log(params.MIN_DISTANCE)
    )

    # Calculate the frequency
    frequency = params.MAX_FREQ - normalized_log * (params.MAX_FREQ - params.MIN_FREQ)

    return frequency


def smooth_distance(previous_distance, next_distance):
    # exponential smoothing
    if next_distance is None:
        return previous_distance
    else:
        return (
            params.DISTANCE_ALPHA * next_distance
            + (1 - params.DISTANCE_ALPHA) * previous_distance
        )


def update_amplitude(previous_amplitude, next_distance):
    if next_distance is None:
        next_amplitude = (1 - params.AMPLITUDE_DECAY) * previous_amplitude
    else:
        next_amplitude = (1 + params.AMPLITUDE_ATTACK) * previous_amplitude
    return np.min([1.0, next_amplitude])


def generate_sine_wave(freq):
    sine_wave = []
    for ii in range(params.CHUNK_LENGTH):
        sine_wave.append(pll.generate_next_point(freq))
    return sine_wave


# this generates one theremin sample at a time, given the previous phase and current frequency
class PLLSineGenerator:
    def __init__(self):
        self.phase = 0

    def generate_next_point(self, freq):
        # Calculate phase increment
        phase_increment = 2 * np.pi * freq / params.SAMPLING_RATE

        # Update phase
        self.phase += phase_increment

        # Keep the phase within the range of 0 to 2π to avoid overflow
        self.phase %= 2 * np.pi

        # Generate sine wave
        return 0.5 * np.sin(self.phase)


pll = PLLSineGenerator()
audio_chunk_seconds = params.CHUNK_LENGTH / params.SAMPLING_RATE


class Theremin:
    def __init__(self):
        self.distance = params.MIN_DISTANCE  # should never be null

        # Audio parameters initial values
        self.amplitude = 1

        # State parameters, initial values
        self.boot_delay_timer = 0  # seconds
        self.boot_sequence_timer = 0  # seconds
        self.shutdown_delay_timer = 0  # seconds
        self.shutdown_sequence_timer = 0  # seconds

    def update(self, past_mode, new_distance):
        """
        past_mode: string, one of "standby", "active", "boot", "shutdown"
        new_distance: distnace in cm, or None

        This function generates the next_mode, freq, and amplitude
        """
        previous_amplitude = self.amplitude

        if (
            new_distance is not None and new_distance > params.MAX_DISTANCE
        ):  # handle wall reflection case
            new_distance = None

        if new_distance is None:
            self.shutdown_delay_timer += audio_chunk_seconds
            self.boot_delay_timer = 0
        else:
            self.shutdown_delay_timer = 0
            self.boot_delay_timer += audio_chunk_seconds

        self.amplitude = update_amplitude(self.amplitude, new_distance)
        self.distance = smooth_distance(self.distance, new_distance)

        if self.amplitude < params.AMPLITUDE_THRESHOLD:
            speed = 0
        else:
            # Normalize self.distance to a range of 0 to 1
            normalized_distance = (self.distance - params.MIN_DISTANCE) / (params.MAX_DISTANCE - params.MIN_DISTANCE)

            # Scale normalized_distance to a range of -1 to 1
            speed = 2 * normalized_distance - 1


        if past_mode == "standby":
            if new_distance is None:
                Theremin.__init__
                next_mode = "standby"
            else:
                if self.boot_delay_timer > params.BOOT_DELAY_TIME:
                    # initialize
                    self.boot_delay_timer = 0
                    self.boot_sequence_timer = 0
                    PLLSineGenerator.__init__
                    next_mode = "boot"
                else:
                    next_mode = "standby"
        elif past_mode == "boot":
            self.boot_sequence_timer += audio_chunk_seconds
            self.amplitude = 1
            if self.boot_sequence_timer > params.BOOT_SEQUENCE_TIME:
                next_mode = "active"
                self.boot_sequence_timer = 0
            else:
                next_mode = "boot"
        elif past_mode == "active":
            if self.shutdown_delay_timer > params.SHUTDOWN_DELAY_TIME:
                self.shutdown_delay_timer = 0
                self.shutdown_sequence_timer = 0
                next_mode = "shutdown"
            else:
                next_mode = "active"
        elif past_mode == "shutdown":
            self.shutdown_sequence_timer += audio_chunk_seconds
            if self.shutdown_sequence_timer > params.SHUTDOWN_SEQUENCE_TIME:
                next_mode = "standby"
                Theremin.__init__
            elif self.boot_delay_timer > params.BOOT_DELAY_TIME:
                next_mode = "active"
            else:
                next_mode = "shutdown"

        freq = map_distance_to_frequency(self.distance)
        # audio out
        amplitude_ramp = np.linspace(
            previous_amplitude, self.amplitude, params.CHUNK_LENGTH
        )
        waveform = np.multiply(amplitude_ramp, np.array(generate_sine_wave(freq)))

        return next_mode, freq, self.amplitude, speed, waveform
