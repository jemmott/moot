class MockDistanceSensor:
    def __init__(self, values):
        self.values = values
        self.index = 0

    @property
    def distance(self):
        if self.index < len(self.values):
            value = self.values[self.index]
            self.index += 1
            return value
        else:
            # Reset the index or handle the empty list as you need
            self.index = 0  # Reset to start
            return self.values[self.index]


def get_distance():
    # Example list of distances the sensor might return
    distance_values = [10, 120, 100, 230, None, None, None, None, 100, 120, 800]
    distance_readings = []
    for d in distance_values:
        distance_readings.extend([d] * 50)

    # Create a mock sensor
    return MockDistanceSensor(distance_readings)

