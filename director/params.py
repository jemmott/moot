# Audio Parameters
SAMPLING_RATE = 44_100  # Hz
CHUNK_LENGTH = 1024

# Distance parameters
MIN_DISTANCE = 5  # cm
MAX_DISTANCE = 800  # cm
DISTANCE_ALPHA = 0.5  # Smoothing factor, between 0 and 1. Closer to 1 gives more weight to recent data.

# Theremin parameters
AMPLITUDE_DECAY = 0.01  # per chunk
AMPLITUDE_ATTACK = 0.1  # per_chunk
MIN_FREQ = 50  # Hz
MAX_FREQ = 1_000  # Hz

# State parameters
BOOT_SEQUENCE_TIME = 3  # seconds of startup sequence
BOOT_DELAY_TIME = 0.5  # seconds of not null distance before startup
SHUTDOWN_SEQUENCE_TIME = 3  # seconds of startup sequence
SHUTDOWN_DELAY_TIME = (
    1  # should be more like 30, but testing # seconds of None distance before shutdown
)
